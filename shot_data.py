from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd


def _parse_scalar(text: str) -> Any:
    """
    Parse common scalar formats used in GOLEM-ish 'parameter' files:
    - float / int
    - otherwise return stripped string
    """
    s = text.strip()
    if s == "":
        return None

    # Try int first (but only if it looks integer-like)
    try:
        if all(c in "+-0123456789" for c in s):
            return int(s)
    except Exception:
        pass

    # Try float
    try:
        return float(s)
    except Exception:
        return s  # fallback to string


@dataclass
class ShotData:
    """
    Accessor for a downloaded shot directory, e.g. shot_51333/

    Usage:
        shot = ShotData("shot_51333")
        L = shot["L_chamber"]          # scalar
        df = shot["dIp_dt.csv"]        # pandas DataFrame
        df2 = shot.df("dIp_dt.csv")    # explicit
    """
    shot_dir: Union[str, Path]

    def __post_init__(self) -> None:
        self.shot_dir = Path(self.shot_dir)
        if not self.shot_dir.exists() or not self.shot_dir.is_dir():
            raise FileNotFoundError(f"Shot directory not found: {self.shot_dir}")

        self._scalars: Dict[str, Any] = {}
        self._dfs: Dict[str, pd.DataFrame] = {}

    def path(self, key: str) -> Path:
        """
        Resolve a key to an on-disk path.
        Keys are typically filenames inside the shot directory (e.g. 'L_chamber', 'dIp_dt.csv').
        """
        p = self.shot_dir / key
        if not p.exists():
            raise KeyError(f"File not found in shot dir: {key} (looked for {p})")
        return p

    def scalar(self, key: str) -> Any:
        """
        Read a single-value file and parse to int/float/str/None.
        Cached after first read.
        """
        if key in self._scalars:
            return self._scalars[key]

        p = self.path(key)
        text = p.read_text(encoding="utf-8", errors="replace")
        val = _parse_scalar(text)
        self._scalars[key] = val
        return val

    def df(self, key: str, **read_csv_kwargs: Any) -> pd.DataFrame:
        """
        Read a CSV file into a pandas DataFrame.
        Cached after first read (per key).
        """
        if key in self._dfs:
            return self._dfs[key]

        p = self.path(key)

        # Reasonable defaults; override as needed
        kwargs = dict(
            comment="#",
            engine="python",
        )
        kwargs.update(read_csv_kwargs)

        df = pd.read_csv(p, **kwargs)
        self._dfs[key] = df
        return df

    def __getitem__(self, key: str) -> Any:
        """
        Convenience:
        - '*.csv' -> DataFrame
        - otherwise -> scalar
        """
        if key.lower().endswith(".csv"):
            return self.df(key)
        return self.scalar(key)

    def keys(self):
        """List files in the shot directory."""
        return sorted([p.name for p in self.shot_dir.iterdir() if p.is_file()])

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default