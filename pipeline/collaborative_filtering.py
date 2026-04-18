import json
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import sparse
from implicit.als import AlternatingLeastSquares
import kagglehub
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Hyperparameters ──────────────────────────────────────────────────
ALPHA = 20                    # confidence scaling factor
MIN_USER_INTERACTIONS = 10    
MIN_GAME_INTERACTIONS = 100   
ALS_FACTORS = 128
ALS_ITERATIONS = 80
ALS_REGULARIZATION = 0.01
RANDOM_STATE = 42

MODEL_DIR = PROJECT_ROOT / "data" / "models" / "cf"

def _load_interactions(path: Path) -> pd.DataFrame:
    """Load and return the raw interactions CSV."""
    print(f"Loading interactions from {path} ...")
    df = pd.read_csv(path, usecols=["user_id", "app_id", "is_recommended", "hours"])
    print(f"  Total interactions: {len(df):,}")
    print(f"  Unique users: {df['user_id'].nunique():,}")
    print(f"  Unique games: {df['app_id'].nunique():,}")
    return df


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove zero-hour, non-recommended, and duplicate interactions."""
    df = df[df["hours"] > 0]
    df = df[df["is_recommended"] == True]
    df = df.drop_duplicates(subset=["user_id", "app_id"])
    print(f"  After cleaning: {len(df):,} interactions")
    return df


def _kcore_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Iterative k-core filtering: repeatedly remove users with fewer than
    MIN_USER_INTERACTIONS and games with fewer than MIN_GAME_INTERACTIONS
    until convergence.
    """
    prev_len = 0
    iteration = 0

    while len(df) != prev_len:
        prev_len = len(df)
        iteration += 1

        user_counts = df["user_id"].value_counts()
        df = df[df["user_id"].isin(user_counts[user_counts >= MIN_USER_INTERACTIONS].index)]

        game_counts = df["app_id"].value_counts()
        df = df[df["app_id"].isin(game_counts[game_counts >= MIN_GAME_INTERACTIONS].index)]

        print(
            f"  Iteration {iteration}: {len(df):,} interactions, "
            f"{df['user_id'].nunique():,} users, {df['app_id'].nunique():,} games"
        )

    num_users = df["user_id"].nunique()
    num_games = df["app_id"].nunique()
    sparsity = 1 - len(df) / (num_users * num_games)
    print(f"  Final: {len(df):,} interactions | {num_users:,} users | {num_games:,} games | Sparsity: {sparsity:.4f}")
    return df


def _build_confidence(df: pd.DataFrame) -> pd.DataFrame:
    """Compute log-transformed hours and Hu et al. (2008) confidence weights."""
    df = df.copy()
    df["hours_log"] = np.log1p(df["hours"].clip(upper=df["hours"].quantile(0.99)))
    df = df[["user_id", "app_id", "hours_log"]].copy()
    df["confidence"] = 1 + ALPHA * df["hours_log"]
    print(f"  Confidence range: {df['confidence'].min():.1f} – {df['confidence'].max():.1f}")
    return df


def _build_sparse_matrix(df: pd.DataFrame) -> tuple[sparse.csr_matrix, dict, dict]:
    """Build a sparse user×item matrix and return the ID mappings."""
    user_ids = df["user_id"].unique()
    item_ids = df["app_id"].unique()

    user_id_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
    item_id_to_idx = {int(iid): idx for idx, iid in enumerate(item_ids)}
    idx_to_item_id = {idx: int(iid) for iid, idx in item_id_to_idx.items()}

    rows = df["user_id"].map(user_id_to_idx).values
    cols = df["app_id"].map(item_id_to_idx).values
    values = df["confidence"].values

    user_item = sparse.csr_matrix(
        (values, (rows, cols)),
        shape=(len(user_ids), len(item_ids)),
    )

    print(f"  User-Item matrix: {user_item.shape}")
    print(f"  Non-zero entries: {user_item.nnz:,}")
    print(f"  Density: {user_item.nnz / (user_item.shape[0] * user_item.shape[1]):.6f}")

    return user_item, item_id_to_idx, idx_to_item_id


def _save_artifacts(
    model: AlternatingLeastSquares,
    idx_to_item_id: dict[int, int],
    item_id_to_idx: dict[int, int],
    hours_p99: float,
) -> None:
    """Save the trained model and ID mappings to disk."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODEL_DIR / "model.npz"
    model.save(str(model_path))
    print(f"  Saved model to {model_path}")

    metadata = {
        "idx_to_item_id": {str(k): v for k, v in idx_to_item_id.items()},
        "item_id_to_idx": {str(k): v for k, v in item_id_to_idx.items()},
        "hours_p99": hours_p99,
        "alpha": ALPHA, # needed for inference confidence calculation
    }
    meta_path = MODEL_DIR / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f)
    print(f"  Saved metadata to {meta_path}")


def cf_model_exists() -> bool:
    """Check if the CF model artifacts already exist on disk."""
    return (MODEL_DIR / "model.npz").exists() and (MODEL_DIR / "metadata.json").exists()


def train_collaborative_filtering() -> None:
    """Full collaborative filtering training pipeline."""
    csv_path = PROJECT_ROOT / "data" / "raw" / "recommendations.csv"

    print("\n══ Collaborative Filtering Pipeline ══")

    if not csv_path.exists():
        print(f"  Dataset not found: {csv_path}. Downloading from Kaggle...")
        download_path = Path(kagglehub.dataset_download("antonkozyriev/game-recommendations-on-steam"))
        print(f"  Dataset downloaded to {download_path}")

        csv_path.parent.mkdir(parents=True, exist_ok=True)

        downloaded_file = download_path / "recommendations.csv"
        if downloaded_file.exists():
            shutil.copy2(downloaded_file, csv_path)
            print(f"  Dataset saved to {csv_path}")
        else:
            raise FileNotFoundError(
                f"Downloaded dataset at {download_path} does not contain recommendations.csv"
            )

    df = _load_interactions(csv_path)

    print("\nCleaning …")
    df = _clean(df)

    print("\nK-core filtering …")
    df = _kcore_filter(df)

    # Store the p99 for hours (needed for inference confidence calculation)
    hours_p99 = float(df["hours"].quantile(0.99))

    print("\nBuilding confidence scores …")
    df_cf = _build_confidence(df)

    print("\nBuilding sparse matrix …")
    user_item, item_id_to_idx, idx_to_item_id = _build_sparse_matrix(df_cf)

    print("\nTraining ALS model …")
    model = AlternatingLeastSquares(
        factors=ALS_FACTORS,
        iterations=ALS_ITERATIONS,
        regularization=ALS_REGULARIZATION,
        random_state=RANDOM_STATE,
    )
    model.fit(user_item)

    print("\nSaving artifacts …")
    _save_artifacts(model, idx_to_item_id, item_id_to_idx, hours_p99)

    print("\n══ Collaborative Filtering Pipeline complete ══\n")