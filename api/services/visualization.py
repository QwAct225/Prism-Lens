import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import glob
import json


class VisualizationService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.data_dir = os.path.join(base_dir, "data")
        self.plots_dir = os.path.join(self.data_dir, "plots")

        self.cleaned_file = os.path.join(self.data_dir, "processed", "arxiv_papers_cleaned.csv")
        self.raw_file = os.path.join(self.data_dir, "raw", "arxiv_papers_raw.csv")
        self.embeddings_file = os.path.join(self.data_dir, "embeddings.npy")

        os.makedirs(self.plots_dir, exist_ok=True)

        self._log_file_status()

    def _log_file_status(self):
        """Log apakah file-file yang dibutuhkan ada"""
        print(f"Checking visualization files:")
        print(f"  Cleaned file: {self.cleaned_file} - Exists: {os.path.exists(self.cleaned_file)}")
        print(f"  Raw file: {self.raw_file} - Exists: {os.path.exists(self.raw_file)}")
        print(f"  Embeddings file: {self.embeddings_file} - Exists: {os.path.exists(self.embeddings_file)}")
        print(f"  Plots directory: {self.plots_dir} - Exists: {os.path.exists(self.plots_dir)}")

    def list_plots(self) -> List[str]:
        """List all available plots"""
        if not os.path.exists(self.plots_dir):
            return []

        plot_files = glob.glob(os.path.join(self.plots_dir, "*.png"))
        return [os.path.basename(f) for f in plot_files]

    def get_plot_path(self, plot_name: str) -> str:
        """Get the file path for a specific plot"""
        return os.path.join(self.plots_dir, plot_name)

    def _load_data(self) -> pd.DataFrame:
        """Load the cleaned papers data"""
        if os.path.exists(self.cleaned_file):
            print(f"Loading data from cleaned file: {self.cleaned_file}")
            return pd.read_csv(self.cleaned_file)
        elif os.path.exists(self.raw_file):
            print(f"Loading data from raw file: {self.raw_file}")
            return pd.read_csv(self.raw_file)

        print("No data file found")
        return pd.DataFrame()

    def _clean_for_json(self, value):
        """Clean value for JSON serialization"""
        if isinstance(value, float):
            if np.isnan(value) or np.isinf(value):
                return None
        return value

    def get_papers(self, limit: int = 10, skip: int = 0,
                   search: Optional[str] = None,
                   sort_by: Optional[str] = None,
                   sort_order: Optional[str] = "asc") -> List[Dict[str, Any]]:
        """Get papers with pagination, searching, and sorting"""
        df = self._load_data()

        if df.empty:
            return []

        column_mapping = {
            'ID': 'id',
            'Title': 'title',
            'Authors': 'authors',
            'Abstract': 'abstract',
            'Journal_Conference_Name': 'journal',
            'Publisher': 'publisher',
            'Year': 'year',
            'DOI': 'doi',
            'Group_Name': 'research_group'
        }

        df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

        # Replace NaN values with None for proper JSON serialization
        df = df.replace({np.nan: None, np.inf: None, -np.inf: None})

        if "authors" in df.columns:
            df["authors"] = df["authors"].apply(
                lambda x: x.split(", ") if isinstance(x, str) else []
            )

        if search:
            search = search.lower()
            # Search in titles and authors
            title_mask = df["title"].str.lower().str.contains(search, na=False)

            if "authors" in df.columns:
                authors_mask = df["authors"].apply(
                    lambda authors: any(search in str(author).lower() for author in authors if author)
                )
                df = df[title_mask | authors_mask]
            else:
                df = df[title_mask]

        if sort_by and sort_by in df.columns:
            ascending = sort_order.lower() == "asc"
            df = df.sort_values(by=sort_by, ascending=ascending)

        # Apply pagination
        df = df.iloc[skip:skip + limit]

        result = []
        for _, row in df.iterrows():
            paper = {}

            for col in df.columns:
                paper[col] = self._clean_for_json(row[col])

            result.append(paper)

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the papers dataset"""
        df = self._load_data()

        if df.empty:
            return {"error": "No data available"}

        # Normalize column names
        if 'Title' in df.columns:
            df = df.rename(columns={'Title': 'title'})
        if 'Authors' in df.columns:
            df = df.rename(columns={'Authors': 'authors'})

        # Basic statistics
        stats = {
            "total_papers": len(df),
            "unique_authors": 0,
            "average_authors_per_paper": 0,
            "average_title_length": 0,
        }

        authors_col = 'authors' if 'authors' in df.columns else 'Authors'
        if authors_col in df.columns:
            all_authors = []
            for authors_str in df[authors_col]:
                if isinstance(authors_str, str):
                    all_authors.extend(authors_str.split(", "))

            stats["unique_authors"] = len(set(all_authors))
            stats["average_authors_per_paper"] = len(all_authors) / len(df) if len(df) > 0 else 0

        title_col = 'title' if 'title' in df.columns else 'Title'
        if title_col in df.columns:
            stats["average_title_length"] = df[title_col].str.len().mean()

        return stats

    def get_embeddings(self, limit: int = 100, skip: int = 0) -> Dict[str, Any]:
        """Get paper embeddings for visualization"""
        if not os.path.exists(self.embeddings_file):
            return {"error": f"Embeddings file not found at {self.embeddings_file}"}

        try:
            embeddings = np.load(self.embeddings_file)
            df = self._load_data()

            if df.empty:
                return {"error": "No paper data available"}

            # Handle mismatch between embeddings and data
            if embeddings.shape[0] != len(df):
                # Ambil data yang dapat diproses (minimum dari keduanya)
                min_count = min(embeddings.shape[0], len(df))

                mismatch_message = f"Embeddings dimension mismatch with data. Embeddings: {embeddings.shape[0]}, Data rows: {len(df)}"
                print(f"WARNING: {mismatch_message}. Using first {min_count} rows.")

                embeddings = embeddings[:min_count]
                df = df.iloc[:min_count]

                if min_count == 0:
                    return {"error": mismatch_message}

            if skip >= len(df):
                return {"error": f"Skip value {skip} exceeds data length {len(df)}"}

            end_idx = min(skip + limit, len(df))
            embeddings = embeddings[skip:end_idx]
            df = df.iloc[skip:end_idx]

            if 'Title' in df.columns:
                df = df.rename(columns={'Title': 'title'})
            if 'ID' in df.columns:
                df = df.rename(columns={'ID': 'id'})

            # Format response
            result = {
                "count": len(embeddings),
                "total_available": min(embeddings.shape[0], len(df)),
                "items": []
            }

            id_col = 'id' if 'id' in df.columns else 'ID'
            title_col = 'title' if 'title' in df.columns else 'Title'

            for i, (embedding, (_, row)) in enumerate(zip(embeddings, df.iterrows())):
                cleaned_embedding = np.nan_to_num(embedding, nan=0.0, posinf=0.0, neginf=0.0).tolist()

                item = {
                    "paper_id": row[id_col] if id_col in row and not pd.isna(row[id_col]) else (skip + i),
                    "title": row[title_col] if not pd.isna(row[title_col]) else "Unknown Title",
                    "embedding": cleaned_embedding
                }
                result["items"].append(item)

            return result

        except Exception as e:
            import traceback
            print(f"Error in get_embeddings: {str(e)}")
            print(traceback.format_exc())
            return {"error": f"Error loading embeddings: {str(e)}"}