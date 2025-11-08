"""
Test script to compare NEW cardiovascular model vs OLD cardiovascular model
"""
import sys
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

# Add the parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.feature_engineering import build_cardiovascular_feature_frame

def load_new_cardiovascular_model():
    """Load the NEW cardiovascular model directly"""
    models_dir = Path(__file__).parent / "app" / "ml" / "models"
    model_path = models_dir / "model_cardiovascular.pkl"
    print(f"Loading NEW model from: {model_path}")
    return joblib.load(model_path)

def load_old_cardiovascular_model():
    """Load the OLD cardiovascular model directly"""
    models_dir = Path(__file__).parent / "app" / "ml" / "models"
    model_path = models_dir / "old_model_cardiovascular.pkl"
    print(f"Loading OLD model from: {model_path}")
    return joblib.load(model_path)

def get_feature_names(model):
    """Extract feature names from the model pipeline"""
    try:
        pipeline = None
        if hasattr(model, "calibrated_classifiers_") and model.calibrated_classifiers_:
            pipeline = model.calibrated_classifiers_[0].estimator
        elif hasattr(model, "estimator"):
            pipeline = model.estimator
        
        if pipeline and hasattr(pipeline, "named_steps"):
            preprocessor = pipeline.named_steps.get("pre")
            if preprocessor:
                try:
                    feature_names_out = preprocessor.get_feature_names_out()
                    return [str(name).split("__", 1)[-1] for name in feature_names_out]
                except:
                    pass
    except Exception as e:
        print(f"Warning: Could not extract feature names: {e}")
    
    return []

def predict_with_model(model, edad, genero, altura_cm, peso_kg, cintura_cm, imc, 
                       glucosa_mgdl, hdl_mgdl, ldl_mgdl, trigliceridos_mgdl):
    """Make prediction with a given model"""
    feature_names = get_feature_names(model)
    
    features_df = build_cardiovascular_feature_frame(
        edad=edad,
        genero=genero,
        imc=imc,
        altura_cm=altura_cm,
        peso_kg=peso_kg,
        circunferencia_cintura=cintura_cm,
        glucosa_mgdl=glucosa_mgdl,
        hdl_mgdl=hdl_mgdl,
        trigliceridos_mgdl=trigliceridos_mgdl,
        ldl_mgdl=ldl_mgdl,
        feature_names=feature_names,
    )
    
    risk_score = float(model.predict_proba(features_df)[0, 1])
    return risk_score

def test_case(case_name, edad, genero, altura_cm, peso_kg, cintura_cm, imc,
              glucosa_mgdl, hdl_mgdl, ldl_mgdl, trigliceridos_mgdl,
              new_model, old_model):
    """Test a single case with both models"""
    print(f"\n{'='*80}")
    print(f"{case_name}")
    print(f"{'='*80}")
    print(f"Patient: {edad}y, {genero}, BMI={imc:.1f}, waist={cintura_cm}cm")
    print(f"Lipids: glucose={glucosa_mgdl}, HDL={hdl_mgdl}, LDL={ldl_mgdl}, trig={trigliceridos_mgdl}")
    print("-" * 80)
    
    # Test NEW model
    try:
        new_score = predict_with_model(
            new_model, edad, genero, altura_cm, peso_kg, cintura_cm, imc,
            glucosa_mgdl, hdl_mgdl, ldl_mgdl, trigliceridos_mgdl
        )
        new_risk_level = "low" if new_score < 0.3 else "moderate" if new_score < 0.6 else "high"
        print(f"NEW Model Score: {new_score:.4f} ({new_risk_level})")
    except Exception as e:
        print(f"NEW Model ERROR: {e}")
        new_score = None
        new_risk_level = "ERROR"
    
    # Test OLD model
    try:
        old_score = predict_with_model(
            old_model, edad, genero, altura_cm, peso_kg, cintura_cm, imc,
            glucosa_mgdl, hdl_mgdl, ldl_mgdl, trigliceridos_mgdl
        )
        old_risk_level = "low" if old_score < 0.3 else "moderate" if old_score < 0.6 else "high"
        print(f"OLD Model Score: {old_score:.4f} ({old_risk_level})")
    except Exception as e:
        print(f"OLD Model ERROR: {e}")
        old_score = None
        old_risk_level = "ERROR"
    
    # Compare
    if new_score is not None and old_score is not None:
        diff = new_score - old_score
        diff_pct = (diff / old_score * 100) if old_score != 0 else float('inf')
        print(f"\nDifference: {diff:+.4f} ({diff_pct:+.1f}%)")
        
        if abs(diff) < 0.05:
            print("⚖️  Models are similar")
        elif new_score > old_score:
            print("⬆️  NEW model predicts HIGHER risk")
        else:
            print("⬇️  NEW model predicts LOWER risk")
    
    return new_score, old_score

def main():
    """Run comparison tests"""
    print("="*80)
    print("CARDIOVASCULAR MODEL COMPARISON: NEW vs OLD")
    print("="*80)
    
    try:
        # Load both models
        new_model = load_new_cardiovascular_model()
        old_model = load_old_cardiovascular_model()
        
        print("\n✓ Both models loaded successfully\n")
        
        results = []
        
        # Test Case 1: Low risk - young, healthy patient
        scores = test_case(
            "TEST 1: LOW RISK - Young, Healthy Patient",
            edad=28, genero="female", altura_cm=165, peso_kg=58, cintura_cm=68,
            imc=21.3, glucosa_mgdl=85, hdl_mgdl=65, ldl_mgdl=100, trigliceridos_mgdl=90,
            new_model=new_model, old_model=old_model
        )
        results.append(("Low Risk", scores[0], scores[1]))
        
        # Test Case 2: Moderate risk - middle-aged with some risk factors
        scores = test_case(
            "TEST 2: MODERATE RISK - Middle-aged with Risk Factors",
            edad=52, genero="male", altura_cm=178, peso_kg=88, cintura_cm=98,
            imc=27.8, glucosa_mgdl=110, hdl_mgdl=42, ldl_mgdl=140, trigliceridos_mgdl=180,
            new_model=new_model, old_model=old_model
        )
        results.append(("Moderate Risk", scores[0], scores[1]))
        
        # Test Case 3: High risk - older with multiple risk factors
        scores = test_case(
            "TEST 3: HIGH RISK - Older with Multiple Risk Factors",
            edad=68, genero="male", altura_cm=172, peso_kg=102, cintura_cm=115,
            imc=34.5, glucosa_mgdl=145, hdl_mgdl=35, ldl_mgdl=180, trigliceridos_mgdl=250,
            new_model=new_model, old_model=old_model
        )
        results.append(("High Risk", scores[0], scores[1]))
        
        # Test Case 4: Very high risk - extreme values
        scores = test_case(
            "TEST 4: VERY HIGH RISK - Extreme Values",
            edad=75, genero="male", altura_cm=170, peso_kg=110, cintura_cm=125,
            imc=38.1, glucosa_mgdl=180, hdl_mgdl=28, ldl_mgdl=200, trigliceridos_mgdl=320,
            new_model=new_model, old_model=old_model
        )
        results.append(("Very High Risk", scores[0], scores[1]))
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY COMPARISON")
        print("="*80)
        print(f"{'Profile':<20} {'NEW Model':<15} {'OLD Model':<15} {'Better?'}")
        print("-"*80)
        
        for profile, new_score, old_score in results:
            if new_score is not None and old_score is not None:
                # For risk assessment, "better" means appropriate sensitivity
                if profile == "Low Risk":
                    better = "Similar" if abs(new_score - old_score) < 0.05 else ("NEW" if new_score < old_score else "OLD")
                else:
                    better = "Similar" if abs(new_score - old_score) < 0.05 else ("NEW" if new_score > old_score else "OLD")
                
                print(f"{profile:<20} {new_score:.4f} ({_get_level(new_score):<8}) {old_score:.4f} ({_get_level(old_score):<8}) {better}")
        
        print("\n" + "="*80)
        print("CONCLUSION")
        print("="*80)
        
        # Calculate average difference
        valid_results = [(n, o) for _, n, o in results if n is not None and o is not None]
        if valid_results:
            avg_new = sum(n for n, o in valid_results) / len(valid_results)
            avg_old = sum(o for n, o in valid_results) / len(valid_results)
            
            print(f"Average NEW score: {avg_new:.4f}")
            print(f"Average OLD score: {avg_old:.4f}")
            print(f"Difference: {avg_new - avg_old:+.4f}")
            
            if avg_new > avg_old * 1.2:
                print("\n✓ NEW model is MORE SENSITIVE (predicts higher risk)")
            elif avg_new < avg_old * 0.8:
                print("\n✓ NEW model is MORE CONSERVATIVE (predicts lower risk)")
            else:
                print("\n✓ NEW and OLD models are SIMILAR")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def _get_level(score):
    """Get risk level from score"""
    if score < 0.3:
        return "low"
    elif score < 0.6:
        return "moderate"
    else:
        return "high"

if __name__ == "__main__":
    main()

