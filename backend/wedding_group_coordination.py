"""
Wedding Group Coordination System
Manages wedding party group consistency and bulk order optimization

Features:
- Group consistency scoring
- Coordination recommendations
- Bulk order processing
- Wedding timeline integration
- KCTmenswear API integration
"""

import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, field

from wedding_sizing_engine import WeddingPartyMember, WeddingDetails, WeddingSizingEngine, WeddingRole, WeddingStyle

logger = logging.getLogger(__name__)

@dataclass
class WeddingGroup:
    """Wedding group containing multiple members"""
    id: str
    wedding_details: WeddingDetails
    members: List[WeddingPartyMember] = field(default_factory=list)
    coordinator: Optional[WeddingPartyMember] = None
    
    def add_member(self, member: WeddingPartyMember):
        """Add member to wedding group"""
        self.members.append(member)
        if not self.coordinator and member.role in [WeddingRole.GROOM, WeddingRole.BEST_MAN]:
            self.coordinator = member
    
    def get_group_size(self) -> int:
        """Get total group size"""
        return len(self.members)
    
    def get_roles(self) -> Dict[str, int]:
        """Get count of each role in group"""
        roles = {}
        for member in self.members:
            role = member.role.value
            roles[role] = roles.get(role, 0) + 1
        return roles

@dataclass 
class GroupConsistencyResult:
    """Result of group consistency analysis"""
    overall_score: float
    coordination_recommendations: List[str]
    size_distribution: Dict[str, int]
    visual_harmony_score: float
    fitting_challenges: List[str]
    bulk_order_optimization: Dict[str, Any]
    timeline_considerations: List[str]

class GroupConsistencyAnalyzer:
    """Analyzes and optimizes wedding party group consistency"""
    
    def __init__(self):
        self.sizing_engine = WeddingSizingEngine()
        
        # Group coordination parameters
        self.coordination_weights = {
            'size_consistency': 0.4,      # How similar sizes are
            'visual_harmony': 0.3,        # Overall visual appeal
            'role_hierarchy': 0.2,        # Proper role-based sizing
            'practical_fitting': 0.1      # Real-world fitting considerations
        }
        
        # Ideal group configurations
        self.ideal_configurations = {
            'groom_centered': {
                'groom_size_variance': 0.5,  # Max size difference from groom
                'best_man_similarity': 0.8,   # Best man should be similar to groom
                'groomsman_variance': 1.0     # Groomsmen can vary more
            },
            'formal_coordination': {
                'style_consistency': 0.9,     # All should match formal style
                'color_coordination': 0.95,   # Tight color coordination
                'fit_consistency': 0.85       # Similar fit preferences
            }
        }
    
    def analyze_group_consistency(self, group: WeddingGroup) -> GroupConsistencyResult:
        """Analyze wedding group for consistency and coordination"""
        
        start_time = time.time()
        
        # Get individual recommendations
        member_recommendations = []
        for member in group.members:
            recommendation = self.sizing_engine.get_role_based_recommendation(
                member, group.wedding_details
            )
            member_recommendations.append({
                'member': member,
                'recommendation': recommendation
            })
        
        # Calculate consistency scores
        size_consistency = self._calculate_size_consistency(member_recommendations)
        visual_harmony = self._calculate_visual_harmony(member_recommendations, group)
        role_hierarchy = self._calculate_role_hierarchy(member_recommendations)
        practical_fitting = self._calculate_practical_fitting(member_recommendations)
        
        # Calculate overall score
        overall_score = (
            size_consistency * self.coordination_weights['size_consistency'] +
            visual_harmony * self.coordination_weights['visual_harmony'] +
            role_hierarchy * self.coordination_weights['role_hierarchy'] +
            practical_fitting * self.coordination_weights['practical_fitting']
        )
        
        # Generate recommendations
        coordination_recommendations = self._generate_coordination_recommendations(
            member_recommendations, group
        )
        
        # Identify challenges
        fitting_challenges = self._identify_fitting_challenges(member_recommendations)
        
        # Optimize bulk order
        bulk_optimization = self._optimize_bulk_order(member_recommendations, group)
        
        # Timeline considerations
        timeline_considerations = self._analyze_timeline_considerations(group)
        
        # Size distribution analysis
        size_distribution = self._analyze_size_distribution(member_recommendations)
        
        analysis_time = time.time() - start_time
        
        logger.info(f"Group consistency analysis completed in {analysis_time:.2f}s for {group.get_group_size()} members")
        
        return GroupConsistencyResult(
            overall_score=round(overall_score, 3),
            coordination_recommendations=coordination_recommendations,
            size_distribution=size_distribution,
            visual_harmony_score=round(visual_harmony, 3),
            fitting_challenges=fitting_challenges,
            bulk_order_optimization=bulk_optimization,
            timeline_considerations=timeline_considerations
        )
    
    def _calculate_size_consistency(self, member_recs: List[Dict]) -> float:
        """Calculate how consistent sizes are within the group"""
        
        if len(member_recs) < 2:
            return 1.0
        
        # Extract numeric sizes
        sizes = []
        for rec in member_recs:
            size_str = rec['recommendation']['size']
            numeric_size = int(size_str[:2])  # Extract number from size like "50R"
            sizes.append(numeric_size)
        
        # Calculate variance
        if len(sizes) == 1:
            return 1.0
        
        size_variance = statistics.variance(sizes)
        max_variance = 16  # Max acceptable variance (4 size difference squared)
        
        # Convert to consistency score (0-1, higher is better)
        consistency_score = max(0, 1 - (size_variance / max_variance))
        
        return consistency_score
    
    def _calculate_visual_harmony(self, member_recs: List[Dict], group: WeddingGroup) -> float:
        """Calculate visual harmony of the group"""
        
        harmony_score = 0.8  # Base harmony score
        
        # Check fit preference consistency
        fit_preferences = [rec['member'].fit_preference for rec in member_recs]
        if len(set(fit_preferences)) == 1:
            harmony_score += 0.1  # Perfect fit consistency
        elif len(set(fit_preferences)) == 2:
            harmony_score += 0.05  # Good fit consistency
        
        # Check role-based sizing harmony
        groom_size = None
        for rec in member_recs:
            if rec['member'].role == WeddingRole.GROOM:
                groom_size = int(rec['recommendation']['size'][:2])
                break
        
        if groom_size:
            # Check how well other roles complement groom
            harmony_adjustments = []
            for rec in member_recs:
                if rec['member'].role != WeddingRole.GROOM:
                    member_size = int(rec['recommendation']['size'][:2])
                    size_diff = abs(member_size - groom_size)
                    
                    if rec['member'].role == WeddingRole.BEST_MAN:
                        # Best man should be very close to groom
                        if size_diff <= 1:
                            harmony_adjustments.append(0.1)
                        elif size_diff <= 2:
                            harmony_adjustments.append(0.05)
                    else:
                        # Other members can vary more
                        if size_diff <= 2:
                            harmony_adjustments.append(0.05)
            
            harmony_score += sum(harmony_adjustments)
        
        # Style-specific harmony
        if group.wedding_details.style in [WeddingStyle.FORMAL, WeddingStyle.BLACK_TIE]:
            # Formal weddings need tighter coordination
            harmony_score *= 0.95
        
        return min(1.0, harmony_score)
    
    def _calculate_role_hierarchy(self, member_recs: List[Dict]) -> float:
        """Calculate how well role hierarchy is maintained in sizing"""
        
        hierarchy_score = 0.9  # Base hierarchy score
        
        groom_rec = None
        best_man_rec = None
        
        # Find groom and best man recommendations
        for rec in member_recs:
            if rec['member'].role == WeddingRole.GROOM:
                groom_rec = rec
            elif rec['member'].role == WeddingRole.BEST_MAN:
                best_man_rec = rec
        
        # Check groom sizing (should be optimal)
        if groom_rec:
            if groom_rec['recommendation']['confidence'] >= 0.8:
                hierarchy_score += 0.05
        
        # Check best man coordination with groom
        if groom_rec and best_man_rec:
            groom_size = int(groom_rec['recommendation']['size'][:2])
            best_man_size = int(best_man_rec['recommendation']['size'][:2])
            size_diff = abs(groom_size - best_man_size)
            
            if size_diff <= 1:
                hierarchy_score += 0.05  # Perfect coordination
        
        return min(1.0, hierarchy_score)
    
    def _calculate_practical_fitting(self, member_recs: List[Dict]) -> float:
        """Calculate practical fitting considerations"""
        
        practical_score = 0.85  # Base practical score
        
        # Check for extreme sizing that might cause issues
        sizes = []
        for rec in member_recs:
            size_str = rec['recommendation']['size']
            numeric_size = int(size_str[:2])
            sizes.append(numeric_size)
        
        # Flag extreme variations
        if sizes:
            min_size, max_size = min(sizes), max(sizes)
            size_range = max_size - min_size
            
            if size_range > 6:  # More than 6 sizes difference
                practical_score -= 0.15
            elif size_range > 4:  # More than 4 sizes difference
                practical_score -= 0.1
            elif size_range > 2:  # More than 2 sizes difference
                practical_score -= 0.05
        
        # Check confidence levels (lower confidence might indicate fitting challenges)
        low_confidence_count = sum(
            1 for rec in member_recs 
            if rec['recommendation']['confidence'] < 0.7
        )
        
        if low_confidence_count > len(member_recs) * 0.3:  # More than 30% low confidence
            practical_score -= 0.1
        
        return max(0.0, practical_score)
    
    def _generate_coordination_recommendations(self, member_recs: List[Dict], 
                                            group: WeddingGroup) -> List[str]:
        """Generate specific coordination recommendations"""
        
        recommendations = []
        
        # Analyze size distribution
        sizes = [int(rec['recommendation']['size'][:2]) for rec in member_recs]
        if sizes:
            size_range = max(sizes) - min(sizes)
            
            if size_range > 4:
                recommendations.append(
                    f"Consider adjusting sizes to reduce range from {min(sizes)}-{max(sizes)} "
                    f"for better group coordination"
                )
            
            # Find the mode (most common size)
            from collections import Counter
            size_counts = Counter(sizes)
            most_common_size = size_counts.most_common(1)[0][0]
            
            recommendations.append(
                f"Consider having {size_counts[most_common_size]} members "
                f"in size {most_common_size} for optimal bulk ordering"
            )
        
        # Role-specific recommendations
        groom_rec = next((rec for rec in member_recs if rec['member'].role == WeddingRole.GROOM), None)
        if groom_rec and groom_rec['recommendation']['confidence'] < 0.8:
            recommendations.append(
                "Groom sizing has low confidence - consider professional fitting consultation"
            )
        
        # Style-specific recommendations
        if group.wedding_details.style == WeddingStyle.FORMAL:
            recommendations.append(
                "For formal wedding: Ensure all members have similar fit preferences for cohesion"
            )
        elif group.wedding_details.style == WeddingStyle.BLACK_TIE:
            recommendations.append(
                "For black tie: Consider slim fit for all male members for elegant appearance"
            )
        
        # Timeline recommendations
        days_until_wedding = (group.wedding_details.date - datetime.now()).days
        if days_until_wedding < 30:
            recommendations.append(
                "Wedding approaching soon - prioritize early ordering and fitting appointments"
            )
        elif days_until_wedding > 180:
            recommendations.append(
                "Plenty of time for multiple fittings - consider seasonal weight changes"
            )
        
        return recommendations
    
    def _identify_fitting_challenges(self, member_recs: List[Dict]) -> List[str]:
        """Identify potential fitting challenges"""
        
        challenges = []
        
        # Check for extreme measurements
        for rec in member_recs:
            member = rec['member']
            if member.height < 160 or member.height > 200:
                challenges.append(
                    f"{member.name}: Extreme height ({member.height}cm) may require special alterations"
                )
            
            if member.weight < 55 or member.weight > 120:
                challenges.append(
                    f"{member.name}: Extreme weight ({member.weight}kg) may affect standard sizing"
                )
        
        # Check for size outliers
        sizes = [int(rec['recommendation']['size'][:2]) for rec in member_recs]
        if sizes:
            median_size = statistics.median(sizes)
            for rec in member_recs:
                member_size = int(rec['recommendation']['size'][:2])
                if abs(member_size - median_size) > 3:
                    challenges.append(
                        f"{rec['member'].name}: Size {member_size} is significantly different from group average"
                    )
        
        return challenges
    
    def _optimize_bulk_order(self, member_recs: List[Dict], group: WeddingGroup) -> Dict[str, Any]:
        """Optimize bulk order for the group"""
        
        # Group by similar sizes
        size_groups = {}
        for rec in member_recs:
            size = rec['recommendation']['size']
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(rec)
        
        # Calculate bulk order benefits
        bulk_order_optimization = {
            'size_groups': {},
            'bulk_savings': {},
            'recommended_ordering': {
                'priority_order': [],
                'fitting_schedule': {},
                'alteration_planning': {}
            }
        }
        
        # Analyze each size group
        for size, members in size_groups.items():
            group_size = len(members)
            bulk_order_optimization['size_groups'][size] = {
                'count': group_size,
                'members': [m['member'].name for m in members],
                'bulk_discount_eligible': group_size >= 3,
                'estimated_savings': (group_size - 1) * 25  # $25 per additional suit
            }
        
        # Create priority ordering (groom first, then others by size groups)
        priority_order = []
        
        # Add groom first
        groom_rec = next((rec for rec in member_recs if rec['member'].role == WeddingRole.GROOM), None)
        if groom_rec:
            priority_order.append({
                'member': groom_rec['member'].name,
                'size': groom_rec['recommendation']['size'],
                'priority': 1,
                'reason': 'Central focus of wedding'
            })
        
        # Add others by size groups (largest groups first)
        sorted_groups = sorted(size_groups.items(), key=lambda x: len(x[1]), reverse=True)
        for size, members in sorted_groups:
            for rec in members:
                if rec['member'].role != WeddingRole.GROOM:
                    priority_order.append({
                        'member': rec['member'].name,
                        'size': rec['recommendation']['size'],
                        'priority': 2,
                        'reason': f'Group size: {len(members)}'
                    })
        
        bulk_order_optimization['recommended_ordering']['priority_order'] = priority_order
        
        return bulk_order_optimization
    
    def _analyze_timeline_considerations(self, group: WeddingGroup) -> List[str]:
        """Analyze timeline considerations for the wedding"""
        
        considerations = []
        wedding_date = group.wedding_details.date
        days_until_wedding = (wedding_date - datetime.now()).days
        
        # Timeline-based recommendations
        if days_until_wedding > 365:
            considerations.append("Over a year away - consider price trends and seasonal sales")
        elif days_until_wedding > 180:
            considerations.append("6+ months - ideal time for initial sizing and ordering")
        elif days_until_wedding > 90:
            considerations.append("3+ months - time for first fitting and adjustments")
        elif days_until_wedding > 30:
            considerations.append("1+ month - final fitting and delivery coordination needed")
        else:
            considerations.append("Less than 1 month - expedite orders and fittings recommended")
        
        # Seasonal considerations
        season = group.wedding_details.season
        if season == 'summer':
            considerations.append("Summer wedding - consider breathable fabrics and lighter colors")
        elif season == 'winter':
            considerations.append("Winter wedding - consider wool fabrics and seasonal colors")
        
        # Style considerations
        style = group.wedding_details.style
        if style == WeddingStyle.FORMAL:
            considerations.append("Formal wedding - allow extra time for formal alterations")
        elif style == WeddingStyle.BLACK_TIE:
            considerations.append("Black tie event - ensure all accessories match perfectly")
        
        return considerations
    
    def _analyze_size_distribution(self, member_recs: List[Dict]) -> Dict[str, int]:
        """Analyze size distribution within the group"""
        
        size_distribution = {}
        for rec in member_recs:
            size = rec['recommendation']['size']
            size_distribution[size] = size_distribution.get(size, 0) + 1
        
        return size_distribution

# Test the group coordination system
if __name__ == "__main__":
    print("👥 Testing Wedding Group Coordination System")
    
    # Create wedding group
    wedding_date = datetime(2025, 6, 15)
    wedding = WeddingDetails(
        date=wedding_date,
        style=WeddingStyle.FORMAL,
        season="summer",
        venue_type="indoor",
        formality_level="formal"
    )
    
    group = WeddingGroup(
        id="wedding_001",
        wedding_details=wedding
    )
    
    # Add wedding party members
    members = [
        WeddingPartyMember("groom", "John Smith", WeddingRole.GROOM, 175, 75, "regular"),
        WeddingPartyMember("best_man", "Mike Johnson", WeddingRole.BEST_MAN, 180, 80, "slim"),
        WeddingPartyMember("groomsman1", "David Brown", WeddingRole.GROOMSMAN, 170, 70, "regular"),
        WeddingPartyMember("groomsman2", "Chris Wilson", WeddingRole.GROOMSMAN, 185, 85, "regular"),
        WeddingPartyMember("father_groom", "Robert Smith", WeddingRole.FATHER_OF_GROOM, 178, 82, "relaxed")
    ]
    
    for member in members:
        group.add_member(member)
    
    # Analyze group consistency
    analyzer = GroupConsistencyAnalyzer()
    result = analyzer.analyze_group_consistency(group)
    
    print(f"\n🎯 Group Consistency Analysis:")
    print(f"Overall Score: {result.overall_score:.1%}")
    print(f"Visual Harmony: {result.visual_harmony_score:.1%}")
    
    print(f"\nSize Distribution:")
    for size, count in result.size_distribution.items():
        print(f"  {size}: {count} members")
    
    print(f"\nCoordination Recommendations:")
    for rec in result.coordination_recommendations:
        print(f"  • {rec}")
    
    print(f"\nBulk Order Optimization:")
    bulk_opt = result.bulk_order_optimization
    print(f"  Size Groups: {len(bulk_opt['size_groups'])}")
    for size, info in bulk_opt['size_groups'].items():
        print(f"    {size}: {info['count']} members, ${info['estimated_savings']} savings")
    
    print(f"\nTimeline Considerations:")
    for consideration in result.timeline_considerations:
        print(f"  • {consideration}")
    
    print(f"\n✅ Group Coordination System test completed!")