import pandas as pd
from src.services.quant.gex_calculator import gex_calculator

def test_gex_calculation():
    print("--- Testing GEX Calculator ---")

    SPOT = 4500.00

    # Mock Data: 1 Call, 1 Put
    data = {
        'strike': [4500, 4400],
        'right': ['C', 'P'],
        'gamma': [0.05, 0.04],
        'open_interest': [1000, 2000]
    }
    df = pd.DataFrame(data)

    print(f"Spot Price: {SPOT}")
    print("Input Chain:\n", df)

    # Run Calculation
    result = gex_calculator.calculate_gex(df, SPOT)

    print("\nResult with GEX:\n", result[['strike', 'right', 'gex']])

    # Validation
    # Call GEX: 0.05 * 1000 * 100 * 0.01 * 4500^2 = 1,012,500,000
    # Put GEX: 0.04 * 2000 * 100 * 0.01 * 4500^2 = 1,620,000,000 (Negative)

    call_gex = result.loc[0, 'gex']
    put_gex = result.loc[1, 'gex']

    if call_gex > 0 and put_gex < 0:
        print("\nSUCCESS: GEX signs are correct (Call+, Put-).")
        print(f"Net GEX: ${call_gex + put_gex:,.2f}")
    else:
        print("\nFAILURE: GEX calculation incorrect.")

if __name__ == "__main__":
    test_gex_calculation()
