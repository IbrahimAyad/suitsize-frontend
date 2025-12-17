"""
Wedding Party Integration for SuitSize.ai
Specialized algorithms for wedding party sizing and group coordination

Features:
- Role-based sizing (groom, groomsmen, fathers, etc.)
- Group consistency scoring
- Wedding-specific recommendations
- Bulk order optimization
- KCTmenswear integration layer
"""

import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class WeddingRole(Enum):
    """Wedding party roles with specific sizing considerations"""
    GROOM = "groom"
    GROOMSMAN = "groomsman" 
    BEST_MAN = "best_man"
    FATHER_OF_BRIDE = "father_of_bride"
    FATHER_OF_GROOM = "father_of_groom"
    USHER = "usher"
    RING_BEARER = "ring_bearer"
    GUESTS = "guests"

class WeddingStyle(Enum):
    """Wedding styles affecting sizing recommendations"""
    FORMAL = "formal"
    SEMI_FORMAL = "semi_formal"
    CASUAL = "casual"
    BLACK_TIE = "black_tie"
    BEACH = "beach"
    OUTDOOR = "outdoor"
    VINTAGE = "vintage"
    MODERN = "modern"

@dataclass
class WeddingPartyMember:
    """Individual wedding party member data"""
    id: str
    name: str
    role: WeddingRole
    height: float  # cm
    weight: float  # kg
    fit_preference: str  # slim/regular/relaxed
    unit: str = 'metric'
    
    # Wedding-specific fields
    age: Optional[int] = None
    body_type: Optional[str] = None
    special_requirements: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role.value,
            'height': self.height,
            'weight': self.weight,
            'fit_preference': self.fit_preference,
            'unit': self.unit,
            'age': self.age,
            'body_type': self.body_type,
            'special_requirements': self.special_requirements or []
        }

@dataclass
class WeddingDetails:
    """Wedding event details affecting sizing"""
    date: datetime
    style: WeddingStyle
    season: str  # spring/summer/fall/winter
    venue_type: str  # indoor/outdoor/beach/church
    formality_level: str  # formal/semi_formal/casual
    color_scheme: Optional[List[str]] = None
    special_requests: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date.isoformat(),
            'style': self.style.value,
            'season': self.season,
            'venue_type': self.venue_type,
            'formality_level': self.formality_level,
            'color_scheme': self.color_scheme or [],
            'special_requests': self.special_requests or []
        }

class WeddingSizingEngine:
    """Core wedding party sizing engine with role-based logic"""
    
    def __init__(self):
        # Wedding-specific size adjustments based on role and style
        self.role_adjustments = {
            WeddingRole.GROOM: {
                'base_multiplier': 1.0,  # Standard sizing
                'confidence_boost': 0.1,  # Groom gets priority
                'style_flexibility': 0.9,  # Less flexible on fit
                'consistency_priority': 'high'
            },
            WeddingRole.BEST_MAN: {
                'base_multiplier': 1.0,
                'confidence_boost': 0.05,
                'style_flexibility': 0.95,
                'consistency_priority': 'high'
            },
            WeddingRole.GROOMSMAN: {
                'base_multiplier': 0.98,  # Slightly smaller to complement groom
                'confidence_boost': 0.0,
                'style_flexibility': 1.0,
                'consistency_priority': 'high'
            },
            WeddingRole.FATHER_OF_BRIDE: {
                'base_multiplier': 1.02,  # Slightly larger for dignity
                'confidence_boost': 0.05,
                'style_flexibility': 1.1,  # More flexible fit options
                'consistency_priority': 'medium'
            },
            WeddingRole.FATHER_OF_GROOM: {
                'base_multiplier': 1.02,
                'confidence_boost': 0.05,
                'style_flexibility': 1.1,
                'consistency_priority': 'medium'
            },
            WeddingRole.USHER: {
                'base_multiplier': 0.99,
                'confidence_boost': 0.0,
                'style_flexibility': 1.0,
                'consistency_priority': 'medium'
            },
            WeddingRole.GUESTS: {
                'base_multiplier': 1.0,
                'confidence_boost': 0.0,
                'style_flexibility': 1.0,
                'consistency_priority': 'low'
            }
        }
        
        # Wedding style impact on sizing
        self.style_impacts = {
            WeddingStyle.FORMAL: {
                'fit_preference_shift': 'regular',  # Bias toward regular fit
                'confidence_boost': 0.05,
                'alteration_probability': 0.3
            },
            WeddingStyle.BLACK_TIE: {
                'fit_preference_shift': 'slim',  # Bias toward slim fit
                'confidence_boost': 0.1,
                'alteration_probability': 0.4
            },
            WeddingStyle.CASUAL: {
                'fit_preference_shift': 'relaxed',  # Bias toward relaxed fit
                'confidence_boost': 0.0,
                'alteration_probability': 0.2
            },
            WeddingStyle.BEACH: {
                'fit_preference_shift': 'relaxed',
                'confidence_boost': 0.05,
                'alteration_probability': 0.2
            },
            WeddingStyle.OUTDOOR: {
                'fit_preference_shift': 'relaxed',
                'confidence_boost': 0.0,
                'alteration_probability': 0.25
            }
        }
    
    def get_role_based_recommendation(self, member: WeddingPartyMember, 
                                    wedding: WeddingDetails) -> Dict[str, Any]:
        """Get sizing recommendation based on wedding role and style"""
        
        role_config = self.role_adjustments[member.role]
        style_config = self.style_impacts.get(wedding.style, {})
        
        # Apply role-based adjustments
        adjusted_height = member.height * role_config['base_multiplier']
        adjusted_weight = member.weight * role_config['base_multiplier']
        
        # Apply style-based fit preference adjustments
        preferred_fit = self._adjust_fit_preference(
            member.fit_preference, 
            style_config.get('fit_preference_shift', member.fit_preference),
            role_config['style_flexibility']
        )
        
        # Generate base recommendation using existing ML engine
        base_recommendation = self._get_base_recommendation(
            adjusted_height, adjusted_weight, preferred_fit, member.unit
        )
        
        # Apply wedding-specific enhancements
        wedding_enhanced = self._apply_wedding_enhancements(
            base_recommendation, member, wedding, role_config, style_config
        )
        
        return wedding_enhanced
    
    def _adjust_fit_preference(self, original_fit: str, style_bias: str, 
                             flexibility: float) -> str:
        """Adjust fit preference based on wedding style and flexibility"""
        
        if original_fit == style_bias:
            return original_fit
        
        # Calculate adjustment probability based on flexibility
        adjustment_probability = abs(1 - flexibility)
        
        import random
        if random.random() < adjustment_probability:
            return style_bias
        else:
            return original_fit
    
    def _get_base_recommendation(self, height: float, weight: float, 
                               fit: str, unit: str) -> Dict[str, Any]:
        """Get base recommendation using the existing ML engine logic"""
        
        # This would integrate with the existing ML engine
        # For now, simulate with enhanced logic
        
        height_cm = height if unit == 'metric' else height * 2.54
        weight_kg = weight if unit == 'metric' else weight * 0.453592
        
        # Enhanced size calculation for wedding parties
        height_weight_ratio = weight_kg / (height_cm / 100)
        
        # Wedding-optimized size ranges
        if fit == 'slim':
            if height_weight_ratio < 0.8:
                size = '38'
            elif height_weight_ratio < 0.9:
                size = '40'
            elif height_weight_ratio < 1.0:
                size = '42'
            elif height_weight_ratio < 1.1:
                size = '44'
            else:
                size = '46'
            size += 'S'
        elif fit == 'relaxed':
            if height_weight_ratio < 0.7:
                size = '40'
            elif height_weight_ratio < 0.8:
                size = '42'
            elif height_weight_ratio < 0.9:
                size = '44'
            elif height_weight_ratio < 1.0:
                size = '46'
            elif height_weight_ratio < 1.1:
                size = '48'
            else:
                size = '50'
            size += 'R'
        else:  # regular
            if height_weight_ratio < 0.75:
                size = '38'
            elif height_weight_ratio < 0.85:
                size = '40'
            elif height_weight_ratio < 0.95:
                size = '42'
            elif height_weight_ratio < 1.05:
                size = '44'
            elif height_weight_ratio < 1.15:
                size = '46'
            elif height_weight_ratio < 1.25:
                size = '48'
            else:
                size = '50'
            size += 'R'
        
        # Length adjustment for tall wedding parties
        if height_cm > 185:
            if height_cm > 200:
                size = size[:-1] + 'L'
        
        # Calculate confidence
        confidence = self._calculate_wedding_confidence(height_cm, weight_kg, fit, size)
        
        return {
            'size': size,
            'confidence': confidence,
            'confidenceLevel': self._get_confidence_level(confidence),
            'bodyType': self._classify_body_type(height_cm, weight_kg),
            'rationale': f"Wedding-optimized {fit} fit recommendation",
            'alterations': self._calculate_wedding_alterations(height_cm, weight_kg, fit, size),
            'measurements': {
                'height_cm': round(height_cm, 1),
                'weight_kg': round(weight_kg, 1),
                'unit': unit
            }
        }
    
    def _apply_wedding_enhancements(self, base_rec: Dict[str, Any], 
                                  member: WeddingPartyMember, 
                                  wedding: WeddingDetails,
                                  role_config: Dict[str, Any],
                                  style_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply wedding-specific enhancements to base recommendation"""
        
        # Add wedding metadata
        enhanced = base_rec.copy()
        enhanced['wedding_role'] = member.role.value
        enhanced['wedding_style'] = wedding.style.value
        enhanced['role_based_adjustment'] = role_config['base_multiplier']
        enhanced['style_influence'] = style_config.get('fit_preference_shift', 'none')
        
        # Add role-specific rationale
        enhanced['wedding_rationale'] = self._generate_wedding_rationale(
            member, wedding, base_rec['size']
        )
        
        # Add wedding-specific alterations
        wedding_alterations = self._get_wedding_specific_alterations(
            member.role, wedding.style, base_rec['size']
        )
        enhanced['alterations'].extend(wedding_alterations)
        
        # Enhance confidence based on role and style
        confidence_boost = (role_config.get('confidence_boost', 0) + 
                          style_config.get('confidence_boost', 0))
        enhanced['confidence'] = min(1.0, enhanced['confidence'] + confidence_boost)
        enhanced['confidenceLevel'] = self._get_confidence_level(enhanced['confidence'])
        
        return enhanced
    
    def _generate_wedding_rationale(self, member: WeddingPartyMember, 
                                  wedding: WeddingDetails, size: str) -> str:
        """Generate wedding-specific rationale"""
        
        role_rationale = {
            WeddingRole.GROOM: f"As the groom, you're the center of attention. The {size} size ensures you'll look polished and confident on your special day.",
            WeddingRole.BEST_MAN: f"As best man, your {size} size complements the groom while maintaining your distinguished presence.",
            WeddingRole.GROOMSMAN: f"As a groomsman, the {size} size ensures you look coordinated with the wedding party while staying comfortable.",
            WeddingRole.FATHER_OF_BRIDE: f"As father of the bride, the {size} size provides the perfect balance of formality and comfort for this special occasion.",
            WeddingRole.FATHER_OF_GROOM: f"As father of the groom, the {size} size ensures you look distinguished and comfortable throughout the celebration.",
            WeddingRole.USHER: f"As an usher, the {size} size helps you look professional while assisting guests.",
        }
        
        style_rationale = f" The {wedding.style.value} wedding style calls for a {member.fit_preference} fit."
        
        return role_rationale.get(member.role, f"The {size} size is recommended for your role and wedding style.") + style_rationale
    
    def _get_wedding_specific_alterations(self, role: WeddingRole, 
                                        style: WeddingStyle, size: str) -> List[str]:
        """Get wedding-specific alteration recommendations"""
        
        alterations = []
        
        # Role-specific alterations
        if role == WeddingRole.GROOM:
            alterations.extend([
                "Wedding_photo_optimization",
                "Comfortable_movement_for_dancing",
                "Vesting_compatibility"
            ])
        elif role == WeddingRole.BEST_MAN:
            alterations.extend([
                "Speech_comfort_adjustment",
                "Photo_coordination_with_groom"
            ])
        elif role in [WeddingRole.FATHER_OF_BRIDE, WeddingRole.FATHER_OF_GROOM]:
            alterations.extend([
                "Extended_comfort_for_long_ceremony",
                "Easy_sitting_adjustment"
            ])
        
        # Style-specific alterations
        if style == WeddingStyle.FORMAL:
            alterations.append("Formal_occasion_enhancements")
        elif style == WeddingStyle.BLACK_TIE:
            alterations.extend([
                "Black_tie_appropriate_fitting",
                "Bow_tie_compatibility"
            ])
        elif style == WeddingStyle.BEACH:
            alterations.append("Breathable_fabric_adjustments")
        
        return alterations
    
    def _calculate_wedding_confidence(self, height: float, weight: float, 
                                    fit: str, size: str) -> float:
        """Calculate confidence specific to wedding scenarios"""
        
        base_confidence = 0.85  # Base wedding confidence
        
        # Height/weight confidence adjustments
        if 170 <= height <= 190 and 65 <= weight <= 95:
            base_confidence += 0.1  # Very typical wedding measurements
        elif height < 160 or height > 200 or weight < 50 or weight > 120:
            base_confidence -= 0.1  # Challenging measurements
        
        # Fit preference confidence
        if fit == 'regular':
            base_confidence += 0.05  # Most common and reliable
        
        return min(1.0, base_confidence)
    
    def _classify_body_type(self, height: float, weight: float) -> str:
        """Classify body type for wedding context"""
        
        bmi = weight / (height / 100) ** 2
        height_weight_ratio = weight / (height / 100)
        
        if bmi < 18.5:
            return "Slim"
        elif bmi > 30:
            return "Broad"
        elif height_weight_ratio > 1.1:
            return "Athletic"
        elif height_weight_ratio < 0.85:
            return "Slender"
        else:
            return "Regular"
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence to level"""
        if confidence >= 0.9:
            return "Very High"
        elif confidence >= 0.8:
            return "High"
        elif confidence >= 0.7:
            return "Medium"
        elif confidence >= 0.6:
            return "Low"
        else:
            return "Very Low"
    
    def _calculate_wedding_alterations(self, height: float, weight: float, 
                                     fit: str, size: str) -> List[str]:
        """Calculate wedding-specific alterations"""
        
        alterations = []
        body_type = self._classify_body_type(height, weight)
        
        # Body type alterations
        if body_type == "Athletic":
            alterations.extend([
                "Shoulder_width_adjustment",
                "Chest_room_optimization"
            ])
        elif body_type == "Broad":
            alterations.extend([
                "Waist_accommodation",
                "Comfortable_movement"
            ])
        elif body_type == "Slim":
            alterations.extend([
                "Tailored_fit",
                "Professional_appearance"
            ])
        
        # Fit-specific alterations
        if fit == 'slim':
            alterations.append("Slim_fit_optimization")
        elif fit == 'relaxed':
            alterations.append("Relaxed_fit_comfort")
        
        # Size-specific alterations
        numeric_size = int(size[:2])
        if numeric_size < 40:
            alterations.append("Petite_sizing_accommodations")
        elif numeric_size > 50:
            alterations.append("Plus_size_accommodations")
        
        return alterations

# Test the wedding sizing engine
if __name__ == "__main__":
    print("💒 Testing Wedding Sizing Engine")
    
    # Initialize engine
    wedding_engine = WeddingSizingEngine()
    
    # Create wedding party members
    groom = WeddingPartyMember(
        id="groom_1",
        name="John Smith",
        role=WeddingRole.GROOM,
        height=175,
        weight=75,
        fit_preference="regular"
    )
    
    best_man = WeddingPartyMember(
        id="best_man_1", 
        name="Mike Johnson",
        role=WeddingRole.BEST_MAN,
        height=180,
        weight=80,
        fit_preference="slim"
    )
    
    groomsman = WeddingPartyMember(
        id="groomsman_1",
        name="David Brown", 
        role=WeddingRole.GROOMSMAN,
        height=170,
        weight=70,
        fit_preference="regular"
    )
    
    # Create wedding details
    wedding = WeddingDetails(
        date=datetime(2025, 6, 15),
        style=WeddingStyle.FORMAL,
        season="summer",
        venue_type="indoor",
        formality_level="formal"
    )
    
    # Test wedding sizing
    members = [groom, best_man, groomsman]
    
    print("\n🎯 Wedding Party Sizing Recommendations:")
    for member in members:
        recommendation = wedding_engine.get_role_based_recommendation(member, wedding)
        print(f"\n{member.name} ({member.role.value}):")
        print(f"  Size: {recommendation['size']}")
        print(f"  Confidence: {recommendation['confidence']:.1%}")
        print(f"  Wedding Rationale: {recommendation['wedding_rationale']}")
        print(f"  Alterations: {recommendation['alterations']}")
    
    print(f"\n✅ Wedding Sizing Engine test completed!")