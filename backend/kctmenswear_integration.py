"""
KCTmenswear Integration Layer for Wedding Party Sizing
Provides seamless integration with KCTmenswear.com for wedding orders

Features:
- KCTmenswear API integration
- Wedding party data synchronization
- Bulk order management
- Order tracking and status updates
- KCT-specific wedding features
"""

import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass, field
from enum import Enum

from wedding_sizing_engine import WeddingPartyMember, WeddingDetails, WeddingSizingEngine, WeddingRole, WeddingStyle
from wedding_group_coordination import WeddingGroup, GroupConsistencyAnalyzer

logger = logging.getLogger(__name__)

class KCTOrderStatus(Enum):
    """KCTmenswear order statuses"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PRODUCTION = "in_production"
    QUALITY_CHECK = "quality_check"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class KCTProductType(Enum):
    """KCT product types for wedding parties"""
    SUIT = "suit"
    TUXEDO = "tuxedo"
    BLAZER = "blazer"
    VEST = "vest"
    SHIRT = "shirt"
    TIE = "tie"
    ACCESSORIES = "accessories"

@dataclass
class KCTOrderItem:
    """Individual item in a KCT order"""
    member_id: str
    member_name: str
    product_type: KCTProductType
    size: str
    fit_preference: str
    color: str = "black"
    special_instructions: str = ""
    alterations_required: List[str] = field(default_factory=list)
    estimated_delivery: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'member_id': self.member_id,
            'member_name': self.member_name,
            'product_type': self.product_type.value,
            'size': self.size,
            'fit_preference': self.fit_preference,
            'color': self.color,
            'special_instructions': self.special_instructions,
            'alterations_required': self.alterations_required,
            'estimated_delivery': self.estimated_delivery.isoformat() if self.estimated_delivery else None
        }

@dataclass
class KCTWeddingOrder:
    """Complete wedding party order for KCTmenswear"""
    order_id: str
    wedding_group: WeddingGroup
    items: List[KCTOrderItem] = field(default_factory=list)
    total_amount: float = 0.0
    bulk_discount: float = 0.0
    status: KCTOrderStatus = KCTOrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    kct_order_number: Optional[str] = None
    
    def add_item(self, item: KCTOrderItem):
        """Add item to the order"""
        self.items.append(item)
        self._recalculate_totals()
    
    def _recalculate_totals(self):
        """Recalculate order totals"""
        # Base pricing (would come from KCT API)
        item_prices = {
            KCTProductType.SUIT: 299.99,
            KCTProductType.TUXEDO: 399.99,
            KCTProductType.BLAZER: 249.99,
            KCTProductType.VEST: 89.99,
            KCTProductType.SHIRT: 49.99,
            KCTProductType.TIE: 29.99,
            KCTProductType.ACCESSORIES: 19.99
        }
        
        subtotal = sum(item_prices.get(item.product_type, 100.0) for item in self.items)
        
        # Bulk discount calculation
        group_size = len(self.wedding_group.members)
        if group_size >= 5:
            self.bulk_discount = subtotal * 0.15  # 15% discount
        elif group_size >= 3:
            self.bulk_discount = subtotal * 0.10  # 10% discount
        else:
            self.bulk_discount = 0.0
        
        self.total_amount = subtotal - self.bulk_discount
        
        # Estimate completion date
        production_days = max(14, group_size * 2)  # Minimum 14 days, plus 2 days per member
        self.estimated_completion = datetime.now() + timedelta(days=production_days)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'order_id': self.order_id,
            'wedding_details': self.wedding_group.wedding_details.to_dict(),
            'items': [item.to_dict() for item in self.items],
            'total_amount': self.total_amount,
            'bulk_discount': self.bulk_discount,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'kct_order_number': self.kct_order_number
        }

class KCTmenswearIntegration:
    """Integration layer for KCTmenswear API and wedding orders"""
    
    def __init__(self, api_base_url: str = "https://api.kctmenswear.com", api_key: str = None):
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.sizing_engine = WeddingSizingEngine()
        self.coordination_analyzer = GroupConsistencyAnalyzer()
        
        # KCT-specific configurations
        self.kct_config = {
            'bulk_discount_threshold': 3,
            'wedding_priority_boost': True,
            'rush_order_upcharge': 0.25,  # 25% upcharge for rush orders
            'standard_production_days': 21,
            'rush_production_days': 14
        }
    
    def create_wedding_order(self, wedding_group: WeddingGroup) -> KCTWeddingOrder:
        """Create a complete wedding order for KCTmenswear"""
        
        logger.info(f"Creating KCT wedding order for group {wedding_group.id}")
        
        # Generate order ID
        order_id = f"WEDDING_{wedding_group.id}_{int(time.time())}"
        
        # Create KCT order
        kct_order = KCTWeddingOrder(
            order_id=order_id,
            wedding_group=wedding_group
        )
        
        # Process each member
        for member in wedding_group.members:
            # Get wedding-specific recommendation
            recommendation = self.sizing_engine.get_role_based_recommendation(
                member, wedding_group.wedding_details
            )
            
            # Determine KCT product type based on role and wedding style
            product_type = self._determine_product_type(member.role, wedding_group.wedding_details.style)
            
            # Create order item
            kct_item = KCTOrderItem(
                member_id=member.id,
                member_name=member.name,
                product_type=product_type,
                size=recommendation['size'],
                fit_preference=member.fit_preference,
                color=self._get_wedding_color(wedding_group.wedding_details),
                special_instructions=self._generate_special_instructions(member, recommendation),
                alterations_required=recommendation['alterations'],
                estimated_delivery=self._estimate_delivery_date(wedding_group)
            )
            
            kct_order.add_item(kct_item)
        
        logger.info(f"Created KCT order with {len(kct_order.items)} items, total: ${kct_order.total_amount:.2f}")
        
        return kct_order
    
    def _determine_product_type(self, role: WeddingRole, style: WeddingStyle) -> KCTProductType:
        """Determine appropriate KCT product type based on role and style"""
        
        # Black tie events require tuxedos
        if style == WeddingStyle.BLACK_TIE:
            return KCTProductType.TUXEDO
        
        # Formal events typically use suits
        elif style in [WeddingStyle.FORMAL, WeddingStyle.SEMI_FORMAL]:
            return KCTProductType.SUIT
        
        # Casual events might use blazers
        elif style == WeddingStyle.CASUAL:
            return KCTProductType.BLAZER
        
        # Default to suits for most wedding roles
        return KCTProductType.SUIT
    
    def _get_wedding_color(self, wedding_details: WeddingDetails) -> str:
        """Determine appropriate color based on wedding details"""
        
        # Default to classic colors based on formality
        if wedding_details.formality_level == "formal":
            return "navy"  # Formal navy instead of black
        elif wedding_details.formality_level == "semi_formal":
            return "charcoal"
        else:
            return "black"
    
    def _generate_special_instructions(self, member: WeddingPartyMember, 
                                     recommendation: Dict[str, Any]) -> str:
        """Generate special instructions for KCT based on member and recommendations"""
        
        instructions = []
        
        # Role-based instructions
        if member.role == WeddingRole.GROOM:
            instructions.append("PRIORITY: Groom order - ensure perfect fit for photos")
        elif member.role == WeddingRole.BEST_MAN:
            instructions.append("Coordinate with groom sizing for optimal photos")
        elif member.role in [WeddingRole.FATHER_OF_BRIDE, WeddingRole.FATHER_OF_GROOM]:
            instructions.append("Comfort fit for long ceremony duration")
        
        # Wedding style instructions
        wedding_style = recommendation.get('wedding_style')
        if wedding_style == 'formal':
            instructions.append("Formal occasion - ensure crisp, professional appearance")
        elif wedding_style == 'black_tie':
            instructions.append("Black tie event - classic, elegant styling required")
        
        # Alteration priority
        if recommendation.get('alterations'):
            high_priority_alts = [
                alt for alt in recommendation['alterations'] 
                if any(keyword in alt.lower() for keyword in ['wedding', 'photo', 'comfort'])
            ]
            if high_priority_alts:
                instructions.append(f"Priority alterations: {', '.join(high_priority_alts)}")
        
        return "; ".join(instructions) if instructions else ""
    
    def _estimate_delivery_date(self, wedding_group: WeddingGroup) -> datetime:
        """Estimate delivery date based on wedding timeline"""
        
        wedding_date = wedding_group.wedding_details.date
        days_until_wedding = (wedding_date - datetime.now()).days
        
        # Standard delivery: 3 weeks before wedding
        standard_delivery = wedding_date - timedelta(days=21)
        
        # Rush delivery: 2 weeks before wedding if needed
        if days_until_wedding < 35:  # Less than 5 weeks
            return wedding_date - timedelta(days=14)
        else:
            return standard_delivery
    
    def submit_order_to_kct(self, kct_order: KCTWeddingOrder) -> Dict[str, Any]:
        """Submit order to KCTmenswear API"""
        
        logger.info(f"Submitting order {kct_order.order_id} to KCTmenswear")
        
        # Prepare API payload
        api_payload = {
            'order_type': 'wedding_party',
            'wedding_details': kct_order.wedding_group.wedding_details.to_dict(),
            'items': [item.to_dict() for item in kct_order.items],
            'billing_info': {
                'bulk_discount': kct_order.bulk_discount,
                'total_amount': kct_order.total_amount,
                'rush_order': self._is_rush_order(kct_order.wedding_group)
            },
            'special_requirements': self._compile_special_requirements(kct_order)
        }
        
        # Submit to KCT API (simulated)
        try:
            # In real implementation, this would make actual API call to KCTmenswear
            # response = requests.post(
            #     f"{self.api_base_url}/orders",
            #     headers={'Authorization': f'Bearer {self.api_key}'},
            #     json=api_payload
            # )
            
            # Simulate successful API response
            simulated_response = {
                'success': True,
                'kct_order_number': f"KCT-{int(time.time())}",
                'status': 'confirmed',
                'estimated_completion': kct_order.estimated_completion.isoformat(),
                'production_start_date': datetime.now().isoformat(),
                'customer_service_contact': 'wedding-orders@kctmenswear.com'
            }
            
            # Update order with KCT response
            kct_order.kct_order_number = simulated_response['kct_order_number']
            kct_order.status = KCTOrderStatus.CONFIRMED
            
            logger.info(f"Order submitted successfully. KCT Order Number: {simulated_response['kct_order_number']}")
            
            return simulated_response
            
        except Exception as e:
            logger.error(f"Failed to submit order to KCTmenswear: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'retry_recommended': True
            }
    
    def _is_rush_order(self, wedding_group: WeddingGroup) -> bool:
        """Determine if this is a rush order"""
        
        days_until_wedding = (wedding_group.wedding_details.date - datetime.now()).days
        return days_until_wedding < 35  # Less than 5 weeks
    
    def _compile_special_requirements(self, kct_order: KCTWeddingOrder) -> List[str]:
        """Compile special requirements for the entire order"""
        
        requirements = []
        
        # Wedding-specific requirements
        wedding = kct_order.wedding_group.wedding_details
        requirements.append(f"Wedding Date: {wedding.date.strftime('%B %d, %Y')}")
        requirements.append(f"Wedding Style: {wedding.style.value}")
        requirements.append(f"Venue: {wedding.venue_type}")
        
        # Group coordination requirements
        group_analysis = self.coordination_analyzer.analyze_group_consistency(kct_order.wedding_group)
        if group_analysis.overall_score < 0.8:
            requirements.append("GROUP COORDINATION: Manual review required for size consistency")
        
        # Bulk order benefits
        if len(kct_order.items) >= self.kct_config['bulk_discount_threshold']:
            requirements.append(f"BULK ORDER: {len(kct_order.items)} items qualify for bulk discount")
        
        # Timeline considerations
        if self._is_rush_order(kct_order.wedding_group):
            requirements.append("RUSH ORDER: Priority production required")
        
        return requirements
    
    def track_order_status(self, kct_order_number: str) -> Dict[str, Any]:
        """Track order status with KCTmenswear"""
        
        logger.info(f"Tracking KCT order status: {kct_order_number}")
        
        try:
            # Simulate order tracking (would be real API call)
            # response = requests.get(
            #     f"{self.api_base_url}/orders/{kct_order_number}/status",
            #     headers={'Authorization': f'Bearer {self.api_key}'}
            # )
            
            # Simulated tracking response
            tracking_data = {
                'kct_order_number': kct_order_number,
                'status': 'in_production',
                'production_stage': 'cutting_and_sewing',
                'estimated_completion': (datetime.now() + timedelta(days=10)).isoformat(),
                'milestones': [
                    {'stage': 'order_confirmed', 'date': datetime.now().isoformat(), 'completed': True},
                    {'stage': 'measurements_reviewed', 'date': (datetime.now() + timedelta(days=1)).isoformat(), 'completed': True},
                    {'stage': 'fabric_selected', 'date': (datetime.now() + timedelta(days=2)).isoformat(), 'completed': True},
                    {'stage': 'cutting_and_sewing', 'date': (datetime.now() + timedelta(days=5)).isoformat(), 'completed': False},
                    {'stage': 'quality_check', 'date': (datetime.now() + timedelta(days=8)).isoformat(), 'completed': False},
                    {'stage': 'packaging', 'date': (datetime.now() + timedelta(days=9)).isoformat(), 'completed': False},
                    {'stage': 'shipped', 'date': (datetime.now() + timedelta(days=10)).isoformat(), 'completed': False}
                ],
                'customer_notifications': True,
                'wedding_priority': True
            }
            
            return tracking_data
            
        except Exception as e:
            logger.error(f"Failed to track order status: {str(e)}")
            return {
                'error': str(e),
                'status': 'unknown'
            }
    
    def get_wedding_order_dashboard(self, kct_order: KCTWeddingOrder) -> Dict[str, Any]:
        """Get comprehensive wedding order dashboard"""
        
        # Get group consistency analysis
        group_analysis = self.coordination_analyzer.analyze_group_consistency(kct_order.wedding_group)
        
        # Calculate order metrics
        total_items = len(kct_order.items)
        bulk_discount_percent = (kct_order.bulk_discount / (kct_order.total_amount + kct_order.bulk_discount)) * 100 if kct_order.total_amount > 0 else 0
        
        dashboard = {
            'order_summary': {
                'kct_order_number': kct_order.kct_order_number,
                'status': kct_order.status.value,
                'total_items': total_items,
                'total_amount': kct_order.total_amount,
                'bulk_discount': kct_order.bulk_discount,
                'bulk_discount_percent': round(bulk_discount_percent, 1),
                'estimated_completion': kct_order.estimated_completion.isoformat() if kct_order.estimated_completion else None
            },
            'group_analysis': {
                'consistency_score': group_analysis.overall_score,
                'visual_harmony': group_analysis.visual_harmony_score,
                'size_distribution': group_analysis.size_distribution,
                'coordination_recommendations': group_analysis.coordination_recommendations
            },
            'wedding_details': kct_order.wedding_group.wedding_details.to_dict(),
            'order_items': [item.to_dict() for item in kct_order.items],
            'timeline': {
                'days_until_wedding': (kct_order.wedding_group.wedding_details.date - datetime.now()).days,
                'production_timeline': self._get_production_timeline(kct_order),
                'fitting_schedule': self._generate_fitting_schedule(kct_order)
            },
            'next_steps': self._get_next_steps(kct_order, group_analysis)
        }
        
        return dashboard
    
    def _get_production_timeline(self, kct_order: KCTWeddingOrder) -> List[Dict[str, str]]:
        """Get production timeline for the order"""
        
        timeline = []
        current_date = datetime.now()
        
        # Order confirmation
        timeline.append({
            'milestone': 'Order Confirmed',
            'date': current_date.isoformat(),
            'status': 'completed',
            'description': 'KCTmenswear has confirmed your wedding party order'
        })
        
        # Measurement review
        timeline.append({
            'milestone': 'Measurements Review',
            'date': (current_date + timedelta(days=1)).isoformat(),
            'status': 'pending',
            'description': 'Our team will review all measurements for accuracy'
        })
        
        # Fabric selection
        timeline.append({
            'milestone': 'Fabric Selection',
            'date': (current_date + timedelta(days=3)).isoformat(),
            'status': 'pending',
            'description': 'Fabrics will be selected based on your wedding style'
        })
        
        # Production start
        timeline.append({
            'milestone': 'Production Start',
            'date': (current_date + timedelta(days=5)).isoformat(),
            'status': 'pending',
            'description': 'Cutting and sewing begins for all items'
        })
        
        # Quality check
        timeline.append({
            'milestone': 'Quality Check',
            'date': (current_date + timedelta(days=12)).isoformat(),
            'status': 'pending',
            'description': 'Final quality inspection before shipping'
        })
        
        return timeline
    
    def _generate_fitting_schedule(self, kct_order: KCTWeddingOrder) -> List[Dict[str, str]]:
        """Generate recommended fitting schedule"""
        
        schedule = []
        wedding_date = kct_order.wedding_group.wedding_details.date
        
        # Initial fitting
        initial_fitting = wedding_date - timedelta(days=45)
        schedule.append({
            'fitting_type': 'Initial Measurement & Fitting',
            'date': initial_fitting.isoformat(),
            'participants': 'All wedding party members',
            'purpose': 'Take measurements and initial fitting',
            'duration': '2-3 hours for full group'
        })
        
        # First adjustment fitting
        first_adjustment = wedding_date - timedelta(days=21)
        schedule.append({
            'fitting_type': 'First Adjustment Fitting',
            'date': first_adjustment.isoformat(),
            'participants': 'Members needing adjustments',
            'purpose': 'Make initial adjustments based on first fitting',
            'duration': '1-2 hours'
        })
        
        # Final fitting
        final_fitting = wedding_date - timedelta(days=7)
        schedule.append({
            'fitting_type': 'Final Fitting & Pickup',
            'date': final_fitting.isoformat(),
            'participants': 'All wedding party members',
            'purpose': 'Final adjustments and pickup',
            'duration': '1 hour per person'
        })
        
        return schedule
    
    def _get_next_steps(self, kct_order: KCTWeddingOrder, group_analysis) -> List[str]:
        """Get recommended next steps for the wedding party order"""
        
        next_steps = []
        
        # Order status-based steps
        if kct_order.status == KCTOrderStatus.PENDING:
            next_steps.append("Confirm order details and submit to KCTmenswear")
        elif kct_order.status == KCTOrderStatus.CONFIRMED:
            next_steps.append("Await measurement review confirmation")
            next_steps.append("Schedule initial fitting appointments")
        
        # Group analysis-based steps
        if group_analysis.overall_score < 0.8:
            next_steps.append("Review coordination recommendations with wedding party")
        
        # Timeline-based steps
        days_until_wedding = (kct_order.wedding_group.wedding_details.date - datetime.now()).days
        if days_until_wedding > 60:
            next_steps.append("Plan fitting schedule 6-8 weeks before wedding")
        elif days_until_wedding > 30:
            next_steps.append("Schedule fitting appointments within 2 weeks")
        else:
            next_steps.append("Expedite order - contact KCT customer service")
        
        return next_steps

# Test the KCT integration
if __name__ == "__main__":
    print("👔 Testing KCTmenswear Integration")
    
    # Create wedding group
    wedding_date = datetime(2025, 7, 15)
    wedding = WeddingDetails(
        date=wedding_date,
        style=WeddingStyle.FORMAL,
        season="summer",
        venue_type="indoor",
        formality_level="formal"
    )
    
    group = WeddingGroup(
        id="wedding_002",
        wedding_details=wedding
    )
    
    # Add wedding party members
    members = [
        WeddingPartyMember("groom", "Alex Thompson", WeddingRole.GROOM, 178, 78, "regular"),
        WeddingPartyMember("best_man", "Jake Wilson", WeddingRole.BEST_MAN, 182, 82, "slim"),
        WeddingPartyMember("groomsman1", "Ryan Davis", WeddingRole.GROOMSMAN, 175, 75, "regular"),
        WeddingPartyMember("groomsman2", "Matt Brown", WeddingRole.GROOMSMAN, 180, 80, "regular"),
        WeddingPartyMember("father_groom", "Steve Thompson", WeddingRole.FATHER_OF_GROOM, 176, 85, "relaxed")
    ]
    
    for member in members:
        group.add_member(member)
    
    # Initialize KCT integration
    kct_integration = KCTmenswearIntegration()
    
    # Create wedding order
    kct_order = kct_integration.create_wedding_order(group)
    print(f"\n📋 Created KCT Order:")
    print(f"Order ID: {kct_order.order_id}")
    print(f"Items: {len(kct_order.items)}")
    print(f"Total: ${kct_order.total_amount:.2f}")
    print(f"Bulk Discount: ${kct_order.bulk_discount:.2f}")
    
    # Submit to KCT (simulated)
    submission_result = kct_integration.submit_order_to_kct(kct_order)
    print(f"\n🚀 KCT Submission Result:")
    print(f"Success: {submission_result.get('success')}")
    print(f"KCT Order Number: {submission_result.get('kct_order_number')}")
    
    # Get order dashboard
    dashboard = kct_integration.get_wedding_order_dashboard(kct_order)
    print(f"\n📊 Order Dashboard:")
    print(f"Group Consistency Score: {dashboard['group_analysis']['consistency_score']:.1%}")
    print(f"Bulk Discount: {dashboard['order_summary']['bulk_discount_percent']:.1f}%")
    print(f"Days Until Wedding: {dashboard['timeline']['days_until_wedding']}")
    
    print(f"\n✅ KCTmenswear Integration test completed!")