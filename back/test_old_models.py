"""
Test script to verify the old models return logical outputs
"""
import sys
from pathlib import Path

# Add the parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.predictor import predict_risk

def test_diabetes_model():
    """Test diabetes model with various risk profiles"""
    print("=" * 80)
    print("TESTING DIABETES MODEL (OLD VERSION)")
    print("=" * 80)
    
    # Test Case 1: Low risk - young, healthy patient
    print("\n1. LOW RISK PATIENT - Young, healthy")
    print("-" * 40)
    result = predict_risk(
        age=25,
        sex="female",
        height_cm=165,
        weight_kg=60,
        waist_cm=70,
        sleep_hours=8,
        smokes_cig_day=0,
        days_mvpa_week=5,
        bmi=22.0,
        systolic_bp=110,
        total_cholesterol=170,
        model_type="diabetes"
    )
    print(f"Score: {result['score']:.4f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Top Drivers: {[d['feature'] for d in result['drivers'][:3]]}")
    
    # Test Case 2: Moderate risk - middle-aged with some risk factors
    print("\n2. MODERATE RISK PATIENT - Middle-aged with risk factors")
    print("-" * 40)
    result = predict_risk(
        age=50,
        sex="male",
        height_cm=175,
        weight_kg=85,
        waist_cm=95,
        sleep_hours=6,
        smokes_cig_day=5,
        days_mvpa_week=2,
        bmi=27.8,
        systolic_bp=135,
        total_cholesterol=220,
        model_type="diabetes"
    )
    print(f"Score: {result['score']:.4f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Top Drivers: {[d['feature'] for d in result['drivers'][:3]]}")
    
    # Test Case 3: High risk - older with multiple risk factors
    print("\n3. HIGH RISK PATIENT - Older with multiple risk factors")
    print("-" * 40)
    result = predict_risk(
        age=65,
        sex="male",
        height_cm=170,
        weight_kg=100,
        waist_cm=110,
        sleep_hours=5,
        smokes_cig_day=20,
        days_mvpa_week=0,
        bmi=34.6,
        systolic_bp=155,
        total_cholesterol=260,
        model_type="diabetes"
    )
    print(f"Score: {result['score']:.4f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Top Drivers: {[d['feature'] for d in result['drivers'][:3]]}")


def test_cardiovascular_model():
    """Test cardiovascular model with various risk profiles"""
    print("\n" + "=" * 80)
    print("TESTING CARDIOVASCULAR MODEL (OLD VERSION)")
    print("=" * 80)
    
    # Test Case 1: Low risk - young, healthy patient
    print("\n1. LOW RISK PATIENT - Young, healthy")
    print("-" * 40)
    result = predict_risk(
        age=28,
        sex="female",
        height_cm=165,
        weight_kg=58,
        waist_cm=68,
        bmi=21.3,
        glucosa_mgdl=85,
        hdl_mgdl=65,
        trigliceridos_mgdl=90,
        ldl_mgdl=100,
        model_type="cardiovascular"
    )
    print(f"Score: {result['score']:.4f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Top Drivers: {[d['feature'] for d in result['drivers'][:3]]}")
    
    # Test Case 2: Moderate risk - middle-aged with some risk factors
    print("\n2. MODERATE RISK PATIENT - Middle-aged with risk factors")
    print("-" * 40)
    result = predict_risk(
        age=52,
        sex="male",
        height_cm=178,
        weight_kg=88,
        waist_cm=98,
        bmi=27.8,
        glucosa_mgdl=110,
        hdl_mgdl=42,
        trigliceridos_mgdl=180,
        ldl_mgdl=140,
        model_type="cardiovascular"
    )
    print(f"Score: {result['score']:.4f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Top Drivers: {[d['feature'] for d in result['drivers'][:3]]}")
    
    # Test Case 3: High risk - older with multiple risk factors
    print("\n3. HIGH RISK PATIENT - Older with multiple risk factors")
    print("-" * 40)
    result = predict_risk(
        age=68,
        sex="male",
        height_cm=172,
        weight_kg=102,
        waist_cm=115,
        bmi=34.5,
        glucosa_mgdl=145,
        hdl_mgdl=35,
        trigliceridos_mgdl=250,
        ldl_mgdl=180,
        model_type="cardiovascular"
    )
    print(f"Score: {result['score']:.4f}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Top Drivers: {[d['feature'] for d in result['drivers'][:3]]}")


def main():
    """Run all tests"""
    try:
        test_diabetes_model()
        test_cardiovascular_model()
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nSUMMARY:")
        print("- Models are loading correctly")
        print("- Predictions are being generated")
        print("- Risk levels are being assigned")
        print("- Drivers are being calculated")
        print("\nCheck the scores above to verify they are logical:")
        print("- Low risk patients should have scores < 0.3")
        print("- Moderate risk patients should have scores 0.3-0.6")
        print("- High risk patients should have scores > 0.6")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

