import json
import logging

import numpy as np
from scipy import sparse
from implicit.cpu.als import AlternatingLeastSquares

from app.core.config import settings

logger = logging.getLogger(__name__)

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
            self._available = (settings.cf_model_dir / "model.npz").exists() and (settings.cf_model_dir / "metadata.json").exists()
            if not self._available:
                logger.warning("CF model artifacts not found at %s. CF recommendations disabled.", settings.cf_model_dir)
        return self._available
    
    def _load(self) -> None:
        """Load model and metadata from disk."""
        logger.info("Loading CF model from %s", settings.cf_model_dir)
        self._model = AlternatingLeastSquares.load(str(settings.cf_model_dir / "model.npz"))
        with open(settings.cf_model_dir / "metadata.json") as f:
            meta = json.load(f)
        self._item_id_to_idx = meta["item_id_to_idx"]
        self._idx_to_item_id = meta["idx_to_item_id"]
        self._hours_p99 = float(meta["hours_p99"])
        self._alpha = float(meta["alpha"])

    def load(self) -> None:
        """Load model and metadata from disk if available."""
        if not self.available:
            return
        self._load()

    def recommend(
        self,
        app_ids: list[int],
        hours_played: list[float],
        top_n: int,
    ) -> list[tuple[int, float]]:
        """
        Return a list of (app_id, score) tuples for a user who played
        n games in `app_ids` for `hours_played` hours, using ALS with
        recalculate_user=True.
        Returns an empty list if the model is unavailable or if all the games
        are not in the CF index.
        """
        if not self.available:
            return []
        
        if self._model is None:
            self._load()

        item_indices = []
        known_hours = []
        for app_id, hours in zip(app_ids, hours_played):
            item_idx = self._item_id_to_idx.get(str(app_id))
            if item_idx is None:
                logger.debug("app_id %s not in CF index - skipping.", app_id)
                continue
            item_indices.append(item_idx)
            known_hours.append(hours)

        if not item_indices:
            logger.warning("None of the provided app_ids are in the CF index.")
            return []
        
        n_items = len(self._item_id_to_idx)
        hours_log = [np.log1p(min(h, self._hours_p99)) for h in known_hours]
        confidence = [1 + self._alpha * h for h in hours_log]
        user_item = sparse.csr_matrix(
            (confidence, ([0]*len(item_indices), item_indices)),
            shape=(1, n_items),
        )

        rec_indices, rec_scores = self._model.recommend(
            userid=0,
            user_items=user_item,
            N=top_n,
            filter_already_liked_items=True,
            recalculate_user=True,
        )

        return [
            (self._idx_to_item_id[str(idx)], float(score))
            for idx, score in zip(rec_indices, rec_scores)
        ]

cf_model = CFModel()