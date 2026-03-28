import json
import logging
from pathlib import Path

import numpy as np
from scipy import sparse
from implicit.als import AlternatingLeastSquares

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = _PROJECT_ROOT / "data" / "models" / "cf"

class CFModel:

    def __init__(self) -> None:
        self._model: AlternatingLeastSquares | None = None
        self._item_id_to_idx: dict[str, int] | None = None  
        self._idx_to_item_id: dict[str, int] | None = None  
        self._hours_p99: float | None = None
        self._alpha: float | None = None
        self._available: bool | None = None  

    @property
    def available(self) -> bool:
        if self._available is None:
            self._available = (MODEL_DIR / "model.npz").exists() and (MODEL_DIR / "metadata.json").exists()
            if not self._available:
                logger.warning("CF model artifacts not found at %s. CF recommendations disabled.", MODEL_DIR)
        return self._available
    
    def _load(self) -> None:
        """Load model and metadata from disk."""
        logger.info("Loading CF model from %s", MODEL_DIR)
        self._model = AlternatingLeastSquares.load(str(MODEL_DIR / "model.npz"))
        with open(MODEL_DIR / "metadata.json") as f:
            meta = json.load(f)
        self._item_id_to_idx = meta["item_id_to_idx"]  
        self._idx_to_item_id = meta["idx_to_item_id"]   
        self._hours_p99 = float(meta["hours_p99"])
        self._alpha = float(meta["alpha"])

    def recommend(
        self,
        app_id: int,
        hours_played: float,
        top_n: int,
    ) -> list[int]:
        """
        Return a list of recommended app_ids for a user who played `app_id`
        for `hours_played` hours, using ALS with recalculate_user=True.
        Returns an empty list if the model is unavailable or the game is not
        in the CF index.
        """
        if not self.available:
            return []
        
        if self._model is None:
            self._load()

        item_idx = self._item_id_to_idx.get(str(app_id))
        if item_idx is None:
            logger.debug("app_id %s not in CF index - skipping CF.", app_id)
            return []
        
        n_items = len(self._item_id_to_idx)
        hours_log = np.log1p(min(hours_played, self._hours_p99))
        confidence = float(1 + self._alpha * hours_log)
        user_item = sparse.csr_matrix(
            ([confidence], ([0], [item_idx])),
            shape=(1, n_items),
        )

        rec_indices, _ = self._model.recommend(
            userid=0,
            user_items=user_item,
            N=top_n,
            filter_already_liked_items=True,
            recalculate_user=True,
        )

        return [self._idx_to_item_id[str(idx)] for idx in rec_indices]