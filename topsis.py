# Conditional NumPy and pandas imports
try:
    import numpy as np
    import pandas as pd
    NUMPY_AVAILABLE = True
except ImportError as e:
    print(f"NumPy/Pandas import failed in topsis.py: {e}")
    NUMPY_AVAILABLE = False
    np = None
    pd = None

from typing import Dict, Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)

def group_subcriterion_topsis(subcriterion_data, fuzzy_numbers, criterion_name=None, application_values=None):
    """
    Performs Fuzzy TOPSIS analysis on subcriteria within a criterion group
    
    Parameters:
    -----------
    subcriterion_data : list 
        List of dicts with subcriterion details including 'id', 'name', 'detail_weight'
    fuzzy_numbers : dict
        Dictionary mapping crisp values to fuzzy triplets
    criterion_name : str, optional
        Name of the criterion group for logging purposes
    application_values : dict, optional
        Dictionary mapping subcriterion ID to actual application values
        
    Returns:
    --------
    pandas.DataFrame 
        DataFrame with subcriterion rankings within the criterion group
    """
    logger.info(f"\n=== Group TOPSIS Analysis for {criterion_name or 'Unknown Group'} ===")
    logger.info(f"Analyzing {len(subcriterion_data)} subcriteria")
    
    if len(subcriterion_data) < 2:
        logger.warning(f"Not enough subcriteria ({len(subcriterion_data)}) for meaningful TOPSIS analysis")
        # Create a simple result with just the original values
        if len(subcriterion_data) == 1:
            return pd.DataFrame({
                'SubCriterion ID': [subcriterion_data[0]['id']],
                'Name': [subcriterion_data[0]['name']],
                'Detail_Weight': [subcriterion_data[0]['detail_weight']],
                'Rank': [1]
            })
        return pd.DataFrame(columns=['SubCriterion ID', 'Name', 'Detail_Weight', 'Rank'])
    
    # Create decision matrix based on application values if provided, 
    # otherwise use detail_weight values like before
    n_alternatives = len(subcriterion_data)
    
    # Create a decision matrix with each subcriterion as an alternative (row)
    # We're using a single column (criterion) for the analysis
    decision_matrix = np.zeros((n_alternatives, 1), dtype=int)
    
    # If we have application values, use them
    if application_values:
        logger.info(f"Using application values for decision matrix")
        for i, sub in enumerate(subcriterion_data):
            # Get application value for this subcriterion if available
            sub_id = sub['id']
            if sub_id in application_values:
                # Ensure score is in 1-7 range
                app_score = application_values[sub_id]
                app_score = min(max(int(app_score), 1), 7)
                decision_matrix[i, 0] = app_score
            else:
                # Fallback to detail_weight based score if no application value
                detail_weight = float(sub['detail_weight'])
                scaled_score = min(max(int(detail_weight * 6) + 1, 1), 7)
                decision_matrix[i, 0] = scaled_score
                logger.warning(f"No application value for subcriterion {sub_id}, using detail_weight")
    else:
        # This is the original behavior - using detail_weight values
        logger.info(f"No application values provided, using detail_weight for decision matrix")
        for i, sub in enumerate(subcriterion_data):
            # Scale the detail weight to the 1-7 range
            detail_weight = float(sub['detail_weight'])
            
            # Scale from typical range of 0-1 to fuzzy scale 1-7
            # We add 1 to ensure non-zero values get at least a score of 1
            # The multiplication by 6 spreads values across our 1-7 scale
            scaled_score = min(max(int(detail_weight * 6) + 1, 1), 7)
            
            decision_matrix[i, 0] = scaled_score
    
    # We use a single weight since we have only one column in our decision matrix
    # The detail_weight values are already used to create the decision matrix
    # All sub-criteria are considered equally important for this group analysis
    weight = np.array([1.0])  # Single weight for the single criterion
    
    logger.info(f"Decision Matrix: {decision_matrix}")
    logger.info(f"Single weight (equal importance): {weight}")
    
    # Calculate using standard fuzzy TOPSIS
    result = fuzzy_topsis(decision_matrix, weight, fuzzy_numbers)
    
    # Create a more detailed result dataframe
    detailed_results = pd.DataFrame({
        'SubCriterion ID': [sub['id'] for sub in subcriterion_data],
        'Name': [sub['name'] for sub in subcriterion_data],
        'Detail_Weight': [sub['detail_weight'] for sub in subcriterion_data],
        'Score': result['Normalized Cᵢ'].values
    })
    
    # Sort by score in descending order and add rank
    detailed_results = detailed_results.sort_values('Score', ascending=False)
    detailed_results['Rank'] = range(1, len(detailed_results) + 1)
    
    logger.info(f"Group TOPSIS Results for {criterion_name or 'Unknown Group'}:\n{detailed_results}")
    
    return detailed_results

def fuzzy_topsis(decision_matrix, weights, fuzzy_numbers):
    """
    Fuzzy TOPSIS Hesaplama Fonksiyonu
    """
    logger.info("\n=== TOPSIS Hesaplama Başlangıcı ===")
    logger.info(f"Karar Matrisi:\n{decision_matrix}")
    logger.info(f"Ağırlıklar:\n{weights}")
    logger.info(f"Fuzzy Sayılar:\n{fuzzy_numbers}")

    # 1️⃣ Bulanık Karar Matrisi Oluşturma
    # Her crisp değeri fuzzy üçlüsüne dönüştür ve düzleştir
    flat_fuzzy_matrix = []
    for row in decision_matrix:
        flat_row = []
        for value in row:
            fuzzy_triple = fuzzy_numbers[value]
            flat_row.extend(fuzzy_triple)  # (l,m,h) değerlerini tek sıraya ekle
        flat_fuzzy_matrix.append(flat_row)

    fuzzy_decision_matrix = np.array(flat_fuzzy_matrix)
    logger.info("\n=== Bulanık Karar Matrisi (Düzleştirilmiş) ===")
    logger.info(f"Shape: {fuzzy_decision_matrix.shape}")
    logger.info(f"Matrix:\n{fuzzy_decision_matrix}")

    # 2️⃣ Normalize Edilmiş Bulanık Karar Matrisi
    n_criteria = len(decision_matrix[0])  # Orijinal kriter sayısı
    normalized_matrix = np.zeros_like(fuzzy_decision_matrix, dtype=float)

    # Her kriter için ayrı ayrı normalizasyon yap
    for i in range(n_criteria):
        # Her kriter için l,m,h indekslerini hesapla
        l_idx = i * 3
        m_idx = i * 3 + 1
        h_idx = i * 3 + 2

        # Her bileşen için maksimum değeri bul
        max_l = np.max(fuzzy_decision_matrix[:, l_idx])
        max_m = np.max(fuzzy_decision_matrix[:, m_idx])
        max_h = np.max(fuzzy_decision_matrix[:, h_idx])

        # Normalizasyon işlemi
        if max_h > 0:  # Sıfıra bölme kontrolü
            normalized_matrix[:, l_idx] = fuzzy_decision_matrix[:, l_idx] / max_h
            normalized_matrix[:, m_idx] = fuzzy_decision_matrix[:, m_idx] / max_h
            normalized_matrix[:, h_idx] = fuzzy_decision_matrix[:, h_idx] / max_h

    logger.info("\n=== Normalize Edilmiş Bulanık Karar Matrisi ===")
    logger.info(f"Shape: {normalized_matrix.shape}")
    logger.info(f"Matrix:\n{normalized_matrix}")

    # 3️⃣ Ağırlıklı Normalize Edilmiş Karar Matrisi
    weighted_matrix = normalized_matrix * weights

    logger.info("\n=== Ağırlıklı Normalize Edilmiş Karar Matrisi ===")
    logger.info(f"Shape: {weighted_matrix.shape}")
    logger.info(f"Matrix:\n{weighted_matrix}")

    # 4️⃣ FPIS ve FNIS Mesafeleri Hesaplama
    # İdeal çözümler
    fpis = np.ones(weighted_matrix.shape[1])    # Her değer için 1
    fnis = np.zeros(weighted_matrix.shape[1])   # Her değer için 0

    # Mesafeleri hesapla
    d_plus = np.sqrt(np.sum((weighted_matrix - fpis) ** 2, axis=1))
    d_minus = np.sqrt(np.sum((weighted_matrix - fnis) ** 2, axis=1))

    logger.info("\n=== FPIS ve FNIS Mesafeleri ===")
    logger.info(f"d+ (FPIS mesafeleri):\n{d_plus}")
    logger.info(f"d- (FNIS mesafeleri):\n{d_minus}")

    # 5️⃣ Yakınlık Katsayıları (Cᵢ)
    total_distances = d_plus + d_minus
    closeness_coefficients = d_minus / total_distances

    logger.info("\n=== Yakınlık Katsayıları ===")
    logger.info(f"Closeness Coefficients:\n{closeness_coefficients}")

    # 6️⃣ Normalize Edilmiş Yakınlık Katsayıları
    sum_coefficients = np.sum(closeness_coefficients)
    if sum_coefficients > 0:
        normalized_coefficients = closeness_coefficients / sum_coefficients
    else:
        normalized_coefficients = np.ones_like(closeness_coefficients) / len(closeness_coefficients)

    logger.info("\n=== Normalize Edilmiş Yakınlık Katsayıları ===")
    logger.info(f"Normalized Coefficients:\n{normalized_coefficients}")

    # Sonuçları DataFrame olarak döndür
    results_df = pd.DataFrame({
        'Alternative': [f'A{i+1}' for i in range(len(decision_matrix))],
        'Cᵢ': closeness_coefficients,
        'Normalized Cᵢ': normalized_coefficients
    })

    logger.info("\n=== Final Results ===")
    logger.info(f"Results DataFrame:\n{results_df}")

    return results_df

# For backward compatibility with existing code
class FuzzyTOPSIS:
    def __init__(self, weights, decision_matrix):
        self.weights = weights
        self.decision_matrix = decision_matrix

    def calculate(self):
        # Convert decision matrix to crisp values for fuzzy_topsis function
        crisp_matrix = np.array(self.decision_matrix)

        # Define fuzzy numbers
        fuzzy_numbers = {
            1: (0, 0, 1),     # Çok Kötü
            2: (0, 1, 3),     # Kötü
            3: (1, 3, 5),     # Orta Kötü
            4: (3, 5, 7),     # Orta
            5: (5, 7, 9),     # Orta İyi
            6: (7, 9, 10),    # İyi
            7: (9, 10, 10)    # Çok İyi
        }

        # Calculate using the new implementation
        results = fuzzy_topsis(crisp_matrix, self.weights, fuzzy_numbers)

        return results['Normalized Cᵢ'].values, {'detailed_results': results}

# Logging ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    # Test verisi
    decision_matrix = np.array([
        [5, 2, 3, 2],  # 1. alternatif
        [7, 7, 5, 4],  # 2. alternatif
        [6, 6, 7, 6],  # 3. alternatif
        [7, 3, 4, 2]   # 4. alternatif
    ])

    # Kriter ağırlıkları (eşit ağırlık)
    weights = np.array([0.25, 0.25, 0.25, 0.25])

    # Fuzzy sayı dönüşüm sözlüğü
    fuzzy_numbers = {
        1: (0, 0, 1),     # Çok Kötü
        2: (0, 1, 3),     # Kötü
        3: (1, 3, 5),     # Orta Kötü
        4: (3, 5, 7),     # Orta
        5: (5, 7, 9),     # Orta İyi
        6: (7, 9, 10),    # İyi
        7: (9, 10, 10)    # Çok İyi
    }

    # Test hesaplaması
    #Using the new class for backward compatibility
    topsis_calculator = FuzzyTOPSIS(weights, decision_matrix)
    normalized_coefficients, detailed_results = topsis_calculator.calculate()

    print("\nTest Sonuçları:")
    print(detailed_results['detailed_results'])