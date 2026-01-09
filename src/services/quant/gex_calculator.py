import pandas as pd
import numpy as np

class GEXCalculator:
    def calculate_gex(self, chain_df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        """
        Calculates Gamma Exposure (GEX) for an options chain.
        Formula: Gamma * OI * 100 * Spot^2 * 0.01
        Sign: Call GEX is positive, Put GEX is negative (Dealer Perspective).
        """
        df = chain_df.copy()

        # Ensure required columns exist
        required = ['gamma', 'open_interest', 'right'] # right: 'C' or 'P'
        if not all(col in df.columns for col in required):
            raise ValueError(f"DataFrame missing columns. Required: {required}")

        # 1. Calculate Raw GEX ($ per 1% move)
        # Factor = 100 (shares) * 0.01 (1% move) * Spot^2
        factor = 100 * 0.01 * (spot_price ** 2)

        df['gex_raw'] = df['gamma'] * df['open_interest'] * factor

        # 2. Apply Sign (Dealer is Short Calls, Short Puts)
        # Dealer Short Call -> Negative Gamma (Short Gamma) -> But we want Dealer Exposure
        # Convention: 
        # Call OI -> Dealers are Short Calls -> Negative Gamma? 
        # Actually, standard GEX convention:
        # Call GEX = Positive (Dealers Long Gamma / Stabilizing)
        # Put GEX = Negative (Dealers Short Gamma / Accelerating)

        df['gex'] = np.where(df['right'] == 'C', df['gex_raw'], -df['gex_raw'])

        return df

gex_calculator = GEXCalculator()
