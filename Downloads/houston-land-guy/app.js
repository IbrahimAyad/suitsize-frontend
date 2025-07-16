// Houston Land Guy - Enhanced JavaScript with Analytics Implementation
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    initNavigation();
    initPathCards();
    initToolCards();
    initMultiStepForm();
    initCalculators();
    initContactForm();
    initAnimations();
    initFormEnhancements();
    initScrollEffects();
    initAnalyticsTracking();
    console.log('Houston Land Guy application initialized successfully!');
}

// Analytics and Conversion Tracking Functions
function initAnalyticsTracking() {
    // Track page sections viewed
    trackSectionViews();
    
    // Track button clicks
    trackButtonClicks();
    
    // Track phone number clicks
    trackPhoneClicks();
    
    // Track form interactions
    trackFormInteractions();
    
    // Track scroll depth
    trackScrollDepth();
    
    // Track time on page
    trackTimeOnPage();
    
    console.log('Analytics tracking initialized');
}

function trackEvent(eventName, parameters = {}) {
    // Google Analytics 4
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, {
            event_category: parameters.category || 'User Interaction',
            event_label: parameters.label || '',
            value: parameters.value || 1,
            custom_parameter_1: parameters.lead_type || '',
            custom_parameter_2: parameters.lead_source || 'website',
            ...parameters
        });
    }
    
    // Facebook Pixel
    if (typeof fbq !== 'undefined') {
        fbq('track', 'CustomEvent', {
            event_name: eventName,
            ...parameters
        });
    }
    
    // Google Tag Manager
    if (typeof window.dataLayer !== 'undefined') {
        window.dataLayer.push({
            event: eventName,
            ...parameters
        });
    }
    
    // Hotjar events
    if (typeof window.hj !== 'undefined') {
        window.hj('event', eventName);
    }
    
    console.log('Event tracked:', eventName, parameters);
}

function trackConversion(conversionType, value = 0, details = {}) {
    const conversionData = {
        category: 'Conversion',
        event_category: 'Lead Generation',
        currency: 'USD',
        value: value,
        conversion_type: conversionType,
        ...details
    };
    
    // Track as conversion event
    trackEvent('conversion', conversionData);
    
    // Facebook Pixel Lead event
    if (typeof fbq !== 'undefined') {
        fbq('track', 'Lead', {
            content_name: conversionType,
            value: value,
            currency: 'USD'
        });
    }
    
    // Track specific conversion types
    switch(conversionType) {
        case 'property_valuation':
            trackEvent('generate_lead', {
                lead_type: 'property_valuation',
                lead_source: 'website_tool',
                ...conversionData
            });
            break;
        case 'contact_form':
            trackEvent('generate_lead', {
                lead_type: 'contact_inquiry',
                lead_source: 'contact_form',
                ...conversionData
            });
            break;
        case 'phone_call':
            trackEvent('generate_lead', {
                lead_type: 'phone_call',
                lead_source: 'website_click',
                ...conversionData
            });
            break;
    }
}

function trackSectionViews() {
    const sections = document.querySelectorAll('section[id], .hero, .contact-section, .investors-section');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionName = entry.target.id || entry.target.className.split(' ')[0];
                trackEvent('section_view', {
                    category: 'Page Engagement',
                    label: sectionName,
                    section_name: sectionName
                });
            }
        });
    }, { threshold: 0.5 });
    
    sections.forEach(section => observer.observe(section));
}

function trackButtonClicks() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn') || e.target.closest('.btn')) {
            const button = e.target.matches('.btn') ? e.target : e.target.closest('.btn');
            const buttonText = button.textContent.trim();
            const buttonContext = getButtonContext(button);
            
            trackEvent('button_click', {
                category: 'User Interaction',
                label: buttonText,
                button_text: buttonText,
                button_context: buttonContext
            });
        }
    });
}

function trackPhoneClicks() {
    document.addEventListener('click', function(e) {
        if (e.target.matches('a[href^="tel:"]') || e.target.closest('a[href^="tel:"]')) {
            const phoneLink = e.target.matches('a[href^="tel:"]') ? e.target : e.target.closest('a[href^="tel:"]');
            const phoneNumber = phoneLink.getAttribute('href').replace('tel:', '');
            
            trackConversion('phone_call', 100, {
                category: 'Lead Generation',
                label: 'Phone Call',
                phone_number: phoneNumber,
                lead_source: 'website_click'
            });
        }
    });
}

function trackFormInteractions() {
    // Track form starts
    document.addEventListener('focus', function(e) {
        if (e.target.matches('input, select, textarea')) {
            const form = e.target.closest('form');
            if (form && !form.dataset.tracked) {
                form.dataset.tracked = 'true';
                const formName = form.id || 'unknown_form';
                
                trackEvent('form_start', {
                    category: 'Form Interaction',
                    label: formName,
                    form_name: formName
                });
            }
        }
    });
    
    // Track form field completions
    document.addEventListener('blur', function(e) {
        if (e.target.matches('input[required], select[required], textarea[required]') && e.target.value) {
            const fieldName = e.target.name || e.target.id || 'unknown_field';
            
            trackEvent('form_field_complete', {
                category: 'Form Interaction',
                label: fieldName,
                field_name: fieldName
            });
        }
    });
}

function trackScrollDepth() {
    let maxScroll = 0;
    const milestones = [25, 50, 75, 90, 100];
    const tracked = new Set();
    
    function updateScrollDepth() {
        const scrollPercent = Math.round((window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100);
        
        if (scrollPercent > maxScroll) {
            maxScroll = scrollPercent;
            
            milestones.forEach(milestone => {
                if (scrollPercent >= milestone && !tracked.has(milestone)) {
                    tracked.add(milestone);
                    trackEvent('scroll_depth', {
                        category: 'Page Engagement',
                        label: `${milestone}%`,
                        value: milestone,
                        scroll_depth: milestone
                    });
                }
            });
        }
    }
    
    window.addEventListener('scroll', debounce(updateScrollDepth, 100));
}

function trackTimeOnPage() {
    let startTime = Date.now();
    let tracked30s = false;
    let tracked60s = false;
    let tracked120s = false;
    
    function checkTimeOnPage() {
        const timeSpent = Math.round((Date.now() - startTime) / 1000);
        
        if (timeSpent >= 30 && !tracked30s) {
            tracked30s = true;
            trackEvent('time_on_page', {
                category: 'Page Engagement',
                label: '30 seconds',
                value: 30
            });
        }
        
        if (timeSpent >= 60 && !tracked60s) {
            tracked60s = true;
            trackEvent('time_on_page', {
                category: 'Page Engagement',
                label: '1 minute',
                value: 60
            });
        }
        
        if (timeSpent >= 120 && !tracked120s) {
            tracked120s = true;
            trackEvent('time_on_page', {
                category: 'Page Engagement',
                label: '2 minutes',
                value: 120
            });
        }
    }
    
    setInterval(checkTimeOnPage, 10000); // Check every 10 seconds
}

function getButtonContext(button) {
    const section = button.closest('section, .hero, .header');
    if (section) {
        return section.id || section.className.split(' ')[0];
    }
    return 'unknown';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Fixed Navigation with proper smooth scrolling
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            
            if (href.startsWith('#')) {
                const targetId = href.substring(1);
                let targetElement = document.getElementById(targetId);
                
                // Handle special cases
                if (targetId === 'home') {
                    targetElement = document.querySelector('.hero') || document.body;
                } else if (targetId === 'contact') {
                    targetElement = document.querySelector('.contact-section') || document.getElementById('contact');
                } else if (targetId === 'investors') {
                    targetElement = document.querySelector('.investors-section') || document.getElementById('investors');
                }
                
                if (targetElement) {
                    const headerHeight = document.querySelector('.header').offsetHeight;
                    let targetPosition = targetElement.offsetTop - headerHeight - 10;
                    
                    // Ensure we don't scroll above the page
                    if (targetPosition < 0) {
                        targetPosition = 0;
                    }
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Header scroll behavior
    const header = document.querySelector('.header');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', function() {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > lastScrollY && currentScrollY > 100) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollY = currentScrollY;
    });
}

// Fixed Path Cards with proper navigation
function initPathCards() {
    const pathCards = document.querySelectorAll('.path-card');
    
    pathCards.forEach(card => {
        const button = card.querySelector('.btn');
        const path = card.getAttribute('data-path');
        
        // Handle card click
        card.addEventListener('click', function(e) {
            if (e.target.classList.contains('btn')) {
                return; // Let button handle its own click
            }
            
            if (path) {
                scrollToSection(path);
            }
        });
        
        // Handle button click
        if (button && path) {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                scrollToSection(path);
            });
        }
        
        // Add accessibility
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'button');
        
        const heading = card.querySelector('h3');
        if (heading) {
            card.setAttribute('aria-label', `Navigate to ${heading.textContent} section`);
        }
    });
}

// Fixed Tool Cards with proper functionality
function initToolCards() {
    const toolCards = document.querySelectorAll('.tool-card');
    
    toolCards.forEach(card => {
        const button = card.querySelector('.btn');
        const tool = card.getAttribute('data-tool');
        
        const handleToolClick = function() {
            switch(tool) {
                case 'valuation':
                    scrollToSection('sellers');
                    setTimeout(() => {
                        const form = document.getElementById('valuationForm');
                        if (form) {
                            form.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 500);
                    break;
                case 'market':
                    showAlert('Market Dashboard: Current Houston land values averaging $75k-$165k per acre. Call (713) 828-3701 for detailed market analysis.', 'info');
                    break;
                case 'development':
                    scrollToSection('developers');
                    break;
                case 'roi':
                    scrollToSection('developers');
                    setTimeout(() => {
                        const calculator = document.getElementById('roiForm');
                        if (calculator) {
                            calculator.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 500);
                    break;
                default:
                    showAlert('Tool functionality coming soon! Call (713) 828-3701 for assistance.', 'info');
            }
        };
        
        card.addEventListener('click', handleToolClick);
        
        if (button) {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                handleToolClick();
            });
        }
    });
}

// Fixed Multi-Step Form with proper validation and navigation
function initMultiStepForm() {
    const form = document.getElementById('valuationForm');
    if (!form) return;
    
    const steps = form.querySelectorAll('.form-step');
    const nextButtons = form.querySelectorAll('.next-step');
    const prevButtons = form.querySelectorAll('.prev-step');
    
    let currentStep = 1;
    const maxSteps = steps.length;
    
    // Show first step
    showStep(1);
    
    // Next button handlers
    nextButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (validateCurrentStep(currentStep)) {
                if (currentStep < maxSteps) {
                    currentStep++;
                    showStep(currentStep);
                }
            }
        });
    });
    
    // Previous button handlers
    prevButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (currentStep > 1) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });
    
    function showStep(stepNumber) {
        steps.forEach((step, index) => {
            step.classList.remove('active');
            if (index === stepNumber - 1) {
                step.classList.add('active');
            }
        });
    }
    
    function validateCurrentStep(step) {
        const currentStepElement = form.querySelector(`[data-step="${step}"]`);
        if (!currentStepElement) return false;
        
        const requiredFields = currentStepElement.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            clearFieldError(field);
            
            if (!field.value.trim()) {
                showFieldError(field, 'This field is required');
                isValid = false;
            } else {
                // Additional validation
                if (field.type === 'email' && !validateEmail(field.value)) {
                    showFieldError(field, 'Please enter a valid email address');
                    isValid = false;
                }
                
                if (field.type === 'tel' && !validatePhone(field.value)) {
                    showFieldError(field, 'Please enter a valid phone number');
                    isValid = false;
                }
                
                if (field.type === 'number' && parseFloat(field.value) <= 0) {
                    showFieldError(field, 'Please enter a valid number greater than 0');
                    isValid = false;
                }
            }
        });
        
        return isValid;
    }
    
    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateCurrentStep(currentStep)) {
            calculatePropertyValue();
        }
    });
}

// FIXED Property Valuation Calculator - ensures results are displayed
function calculatePropertyValue() {
    const form = document.getElementById('valuationForm');
    const formData = new FormData(form);
    const resultDiv = document.getElementById('valuationResult');
    
    if (!form || !resultDiv) {
        console.error('Form or result div not found');
        return;
    }
    
    const valueDisplay = resultDiv.querySelector('.value-amount');
    if (!valueDisplay) {
        console.error('Value display element not found');
        return;
    }
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Calculating...';
    submitButton.disabled = true;
    
    setTimeout(() => {
        try {
            // Enhanced valuation calculation
            const propertyType = formData.get('propertyType');
            const size = parseFloat(formData.get('size')) || 0;
            const location = formData.get('location') || '';
            const currentUse = formData.get('currentUse');
            const timeline = formData.get('timeline');
            
            // Base price per acre based on property type
            const basePrices = {
                'Residential Land': 95000,
                'Commercial Land': 165000,
                'Industrial Land': 75000,
                'Raw Land': 45000,
                'Agricultural Land': 35000,
                'Development Site': 135000
            };
            
            let basePrice = basePrices[propertyType] || 75000;
            
            // Adjust for current use
            const useMultipliers = {
                'Vacant': 1.0,
                'Agricultural': 0.8,
                'Residential': 1.2,
                'Commercial': 1.4,
                'Industrial': 1.1
            };
            
            basePrice *= useMultipliers[currentUse] || 1.0;
            
            // Location adjustments for Houston areas
            const locationLower = location.toLowerCase();
            if (locationLower.includes('downtown') || locationLower.includes('midtown')) {
                basePrice *= 1.8;
            } else if (locationLower.includes('galleria') || locationLower.includes('uptown')) {
                basePrice *= 1.6;
            } else if (locationLower.includes('woodlands') || locationLower.includes('katy') || locationLower.includes('sugar land')) {
                basePrice *= 1.4;
            } else if (locationLower.includes('spring') || locationLower.includes('pearland')) {
                basePrice *= 1.2;
            }
            
            // Timeline adjustment
            const timelineMultipliers = {
                'Immediate': 0.95,
                '30 days': 0.98,
                '90 days': 1.0,
                '6 months': 1.02,
                '1 year+': 1.05
            };
            
            basePrice *= timelineMultipliers[timeline] || 1.0;
            
            // Size efficiency adjustment
            if (size > 100) {
                basePrice *= 0.9;
            } else if (size > 50) {
                basePrice *= 0.95;
            } else if (size < 1) {
                basePrice *= 1.1;
            }
            
            // Calculate total value with some realistic variance
            const totalValue = Math.round(basePrice * size);
            const variance = 0.05; // 5% variance
            const randomFactor = 1 + (Math.random() - 0.5) * variance;
            const finalValue = Math.round(totalValue * randomFactor);
            
            // Ensure minimum value
            const displayValue = Math.max(finalValue, 10000);
            
            // Display result
            valueDisplay.textContent = formatCurrency(displayValue);
            
            // Hide form and show result
            form.style.display = 'none';
            resultDiv.classList.remove('hidden');
            resultDiv.style.display = 'block';
            
            // Store lead data
            storeLeadData(formData, displayValue);
            
            // Track conversion
            trackConversion('property_valuation', displayValue, {
                property_type: propertyType,
                property_size: size,
                location: location,
                estimated_value: displayValue,
                lead_source: 'valuation_tool'
            });
            
            // Reset button state
            submitButton.textContent = originalText;
            submitButton.disabled = false;
            
            // Scroll to result
            setTimeout(() => {
                resultDiv.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }, 200);
            
            // Show success message
            showAlert('Property valuation completed! Call (713) 828-3701 to discuss your cash offer.', 'success');
            
        } catch (error) {
            console.error('Error in property valuation:', error);
            showAlert('Error calculating property value. Please try again or call (713) 828-3701.', 'error');
            
            // Reset button state
            submitButton.textContent = originalText;
            submitButton.disabled = false;
        }
        
    }, 2000);
}

// Fixed Calculator Functions
function initCalculators() {
    const roiForm = document.getElementById('roiForm');
    const investmentForm = document.getElementById('investmentForm');
    
    if (roiForm) {
        roiForm.addEventListener('submit', function(e) {
            e.preventDefault();
            calculateROI();
        });
    }
    
    if (investmentForm) {
        investmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            calculateInvestmentReturns();
        });
    }
}

// Fixed ROI Calculator
async function calculateROI() {
    const form = document.getElementById('roiForm');
    const formData = new FormData(form);
    const resultDiv = document.getElementById('roiResult');
    
    if (!form || !resultDiv) return;
    
    const landCost = parseFloat(formData.get('landCost')) || 0;
    const developmentCost = parseFloat(formData.get('developmentCost')) || 0;
    const projectedSalePrice = parseFloat(formData.get('projectedSalePrice')) || 0;
    const timeline = formData.get('timeline');
    
    if (landCost <= 0 || developmentCost <= 0 || projectedSalePrice <= 0) {
        showAlert('Please enter valid amounts for all fields', 'error');
        return;
    }
    
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Calculating...';
    submitButton.disabled = true;
    
    setTimeout(() => {
        const totalInvestment = landCost + developmentCost;
        const projectedProfit = projectedSalePrice - totalInvestment;
        const roiPercentage = (projectedProfit / totalInvestment) * 100;
        
        // Calculate annualized return
        const timelineYears = {
            '6 months': 0.5,
            '1 year': 1,
            '18 months': 1.5,
            '2 years': 2,
            '3+ years': 3
        };
        
        const years = timelineYears[timeline] || 1;
        const annualizedReturn = roiPercentage / years;
        
        // Send calculation to backend
        try {
            const response = await fetch('/api/roi-calculation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ landCost, developmentCost, projectedSalePrice, timeline })
            });
            
            const result = await response.json();
            
            if (result.success) {
                const { results } = result;
                
                // Display results from backend
                const elements = {
                    totalInvestment: document.getElementById('totalInvestment'),
                    projectedProfit: document.getElementById('projectedProfit'),
                    roiPercentage: document.getElementById('roiPercentage'),
                    annualizedReturn: document.getElementById('annualizedReturn')
                };
                
                if (elements.totalInvestment) elements.totalInvestment.textContent = formatCurrency(results.totalInvestment);
                if (elements.projectedProfit) elements.projectedProfit.textContent = formatCurrency(results.projectedProfit);
                if (elements.roiPercentage) elements.roiPercentage.textContent = results.roiPercentage + '%';
                if (elements.annualizedReturn) elements.annualizedReturn.textContent = results.annualizedReturn + '%';
                
                // Color coding
                const color = results.roiPercentage > 30 ? '#50C878' : results.roiPercentage > 20 ? '#2E8B57' : results.roiPercentage > 10 ? '#8A9A5B' : '#D4AF37';
                if (elements.roiPercentage) elements.roiPercentage.style.color = color;
                if (elements.annualizedReturn) elements.annualizedReturn.style.color = color;
                
                resultDiv.classList.remove('hidden');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error calculating ROI:', error);
            
            // Fallback to local calculation
            const elements = {
                totalInvestment: document.getElementById('totalInvestment'),
                projectedProfit: document.getElementById('projectedProfit'),
                roiPercentage: document.getElementById('roiPercentage'),
                annualizedReturn: document.getElementById('annualizedReturn')
            };
            
            if (elements.totalInvestment) elements.totalInvestment.textContent = formatCurrency(totalInvestment);
            if (elements.projectedProfit) elements.projectedProfit.textContent = formatCurrency(projectedProfit);
            if (elements.roiPercentage) elements.roiPercentage.textContent = roiPercentage.toFixed(1) + '%';
            if (elements.annualizedReturn) elements.annualizedReturn.textContent = annualizedReturn.toFixed(1) + '%';
            
            // Color coding
            const color = roiPercentage > 30 ? '#50C878' : roiPercentage > 20 ? '#2E8B57' : roiPercentage > 10 ? '#8A9A5B' : '#D4AF37';
            if (elements.roiPercentage) elements.roiPercentage.style.color = color;
            if (elements.annualizedReturn) elements.annualizedReturn.style.color = color;
            
            resultDiv.classList.remove('hidden');
        }
        
        // Reset button
        submitButton.textContent = originalText;
        submitButton.disabled = false;
        
        // Scroll to result
        setTimeout(() => {
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
        
        showAlert('ROI calculation completed! Call (713) 828-3701 to discuss development opportunities.', 'success');
        
    }, 1500);
}

// Fixed Investment Returns Calculator
async function calculateInvestmentReturns() {
    const form = document.getElementById('investmentForm');
    const formData = new FormData(form);
    const resultDiv = document.getElementById('investmentResult');
    
    if (!form || !resultDiv) return;
    
    const investmentAmount = parseFloat(formData.get('investmentAmount')) || 0;
    const returnRate = parseFloat(formData.get('returnRate')) || 0;
    const timeline = parseFloat(formData.get('timeline')) || 0;
    
    if (investmentAmount <= 0 || returnRate <= 0 || timeline <= 0) {
        showAlert('Please enter valid amounts for all fields', 'error');
        return;
    }
    
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Calculating...';
    submitButton.disabled = true;
    
    setTimeout(() => {
        // Calculate compound returns
        const annualReturn = returnRate / 100;
        const projectedValue = investmentAmount * Math.pow(1 + annualReturn, timeline);
        const totalReturn = projectedValue - investmentAmount;
        const annualReturnAmount = totalReturn / timeline;
        
        // Send calculation to backend
        try {
            const response = await fetch('/api/investment-calculation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ investmentAmount, returnRate, timeline })
            });
            
            const result = await response.json();
            
            if (result.success) {
                const { results } = result;
                
                // Display results from backend
                const elements = {
                    initialInvestment: document.getElementById('initialInvestment'),
                    projectedValue: document.getElementById('projectedValue'),
                    totalReturn: document.getElementById('totalReturn'),
                    annualReturn: document.getElementById('annualReturn')
                };
                
                if (elements.initialInvestment) elements.initialInvestment.textContent = formatCurrency(results.initialInvestment);
                if (elements.projectedValue) elements.projectedValue.textContent = formatCurrency(results.projectedValue);
                if (elements.totalReturn) elements.totalReturn.textContent = formatCurrency(results.totalReturn);
                if (elements.annualReturn) elements.annualReturn.textContent = formatCurrency(results.annualReturn);
                
                resultDiv.classList.remove('hidden');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Error calculating investment returns:', error);
            
            // Fallback to local calculation
            const elements = {
                initialInvestment: document.getElementById('initialInvestment'),
                projectedValue: document.getElementById('projectedValue'),
                totalReturn: document.getElementById('totalReturn'),
                annualReturn: document.getElementById('annualReturn')
            };
            
            if (elements.initialInvestment) elements.initialInvestment.textContent = formatCurrency(investmentAmount);
            if (elements.projectedValue) elements.projectedValue.textContent = formatCurrency(projectedValue);
            if (elements.totalReturn) elements.totalReturn.textContent = formatCurrency(totalReturn);
            if (elements.annualReturn) elements.annualReturn.textContent = formatCurrency(annualReturnAmount);
            
            resultDiv.classList.remove('hidden');
        }
        
        // Reset button
        submitButton.textContent = originalText;
        submitButton.disabled = false;
        
        // Scroll to result
        setTimeout(() => {
            resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
        
        showAlert('Investment projection completed! Call (713) 828-3701 to discuss investment opportunities.', 'success');
        
    }, 1500);
}

// Fixed Contact Form
function initContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Validate form
            if (!validateForm(this)) {
                return;
            }
            
            // Show loading state
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            // Simulate form submission
            setTimeout(() => {
                // Track conversion
                trackConversion('contact_form', 50, {
                    interest: formData.get('interest'),
                    lead_source: 'contact_form'
                });
                
                showAlert('Thank you for your message! We will contact you within 24 hours.', 'success');
                this.reset();
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                
                // Store contact data
                storeContactData(formData);
                
            }, 2000);
        });
    }
}

// Form Enhancement Functions
function initFormEnhancements() {
    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    });
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && !validateEmail(this.value)) {
                showFieldError(this, 'Please enter a valid email address');
            } else {
                clearFieldError(this);
            }
        });
    });
    
    // Number input validation
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            if (this.value && value <= 0) {
                this.setCustomValidity('Please enter a number greater than 0');
            } else {
                this.setCustomValidity('');
            }
        });
    });
}

// Advanced Animation and Scroll Effects
function initAnimations() {
    // Enhanced Intersection Observer with multiple animation types
    const observerOptions = {
        threshold: [0.1, 0.3, 0.5, 0.7],
        rootMargin: '-20px 0px -20px 0px'
    };
    
    const animationObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            const element = entry.target;
            const animationType = element.dataset.animation || 'fade-in';
            
            if (entry.isIntersecting) {
                element.classList.add('visible');
                
                // Add specific animation classes based on type
                switch(animationType) {
                    case 'slide-up':
                        element.style.transform = 'translateY(0)';
                        element.style.opacity = '1';
                        break;
                    case 'slide-left':
                        element.style.transform = 'translateX(0)';
                        element.style.opacity = '1';
                        break;
                    case 'slide-right':
                        element.style.transform = 'translateX(0)';
                        element.style.opacity = '1';
                        break;
                    case 'scale-in':
                        element.style.transform = 'scale(1)';
                        element.style.opacity = '1';
                        break;
                    case 'rotate-in':
                        element.style.transform = 'rotate(0deg) scale(1)';
                        element.style.opacity = '1';
                        break;
                    case 'stagger':
                        staggerAnimation(element);
                        break;
                    default:
                        element.style.opacity = '1';
                        element.style.transform = 'translateY(0)';
                }
                
                // Track animation completion
                trackEvent('animation_complete', {
                    category: 'User Experience',
                    label: animationType,
                    element_type: element.tagName.toLowerCase(),
                    element_class: element.className.split(' ')[0]
                });
            }
        });
    }, observerOptions);
    
    // Progressive reveal for different sections
    initProgressiveReveal(animationObserver);
    
    // Parallax scrolling effects
    initParallaxEffects();
    
    // Advanced hover interactions
    initAdvancedHoverEffects();
    
    // Scroll-based counter animations
    initCounterAnimations();
    
    // Dynamic background effects
    initDynamicBackgrounds();
}

function initProgressiveReveal(observer) {
    // Hero section elements
    const heroElements = document.querySelectorAll('.hero-content h1, .hero-content p, .trust-stat');
    heroElements.forEach((element, index) => {
        element.dataset.animation = 'slide-up';
        element.style.transitionDelay = `${index * 0.2}s`;
        element.classList.add('fade-in');
        observer.observe(element);
    });
    
    // Path cards with stagger effect
    const pathCards = document.querySelectorAll('.path-card');
    pathCards.forEach((card, index) => {
        card.dataset.animation = 'stagger';
        card.style.animationDelay = `${index * 0.15}s`;
        card.classList.add('fade-in');
        observer.observe(card);
    });
    
    // Steps with sequential reveal
    const stepCards = document.querySelectorAll('.step-card');
    stepCards.forEach((step, index) => {
        step.dataset.animation = 'slide-left';
        step.style.transitionDelay = `${index * 0.1}s`;
        step.classList.add('fade-in');
        observer.observe(step);
    });
    
    // Tools with scale-in effect
    const toolCards = document.querySelectorAll('.tool-card');
    toolCards.forEach((tool, index) => {
        tool.dataset.animation = 'scale-in';
        tool.style.transitionDelay = `${index * 0.1}s`;
        tool.classList.add('fade-in');
        observer.observe(tool);
    });
    
    // Benefits with rotate-in effect
    const benefitCards = document.querySelectorAll('.benefit-card');
    benefitCards.forEach((benefit, index) => {
        benefit.dataset.animation = 'rotate-in';
        benefit.style.transitionDelay = `${index * 0.08}s`;
        benefit.classList.add('fade-in');
        observer.observe(benefit);
    });
    
    // Other elements
    const otherElements = document.querySelectorAll(`
        .property-type, .service-card, .testimonial, .process-step, 
        .feature, .opportunity-item, .contact-method
    `);
    
    otherElements.forEach((element, index) => {
        element.dataset.animation = 'fade-in';
        element.style.transitionDelay = `${(index % 3) * 0.1}s`;
        element.classList.add('fade-in');
        observer.observe(element);
    });
}

function staggerAnimation(element) {
    const children = element.children;
    Array.from(children).forEach((child, index) => {
        setTimeout(() => {
            child.style.opacity = '1';
            child.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.hero-overlay, .section-header');
    
    function updateParallax() {
        const scrolled = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const rate = scrolled * -0.5;
            element.style.transform = `translateY(${rate}px)`;
        });
    }
    
    // Use requestAnimationFrame for smooth parallax
    let ticking = false;
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', () => {
        requestTick();
        ticking = false;
    });
}

function initAdvancedHoverEffects() {
    // Enhanced card hover effects
    const cards = document.querySelectorAll('.path-card, .tool-card, .step-card, .service-card, .benefit-card');
    
    cards.forEach(card => {
        let hoverTimeout;
        
        card.addEventListener('mouseenter', function(e) {
            clearTimeout(hoverTimeout);
            
            // Add glow effect
            this.style.boxShadow = `
                0 12px 40px rgba(46, 111, 64, 0.2),
                0 0 0 1px rgba(80, 200, 120, 0.3),
                0 0 20px rgba(80, 200, 120, 0.1)
            `;
            
            // Subtle scale and rotate
            this.style.transform = 'translateY(-8px) scale(1.02) rotate(0.5deg)';
            
            // Animate child elements
            const icon = this.querySelector('.path-icon, .tool-icon, .service-icon');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(-5deg)';
                icon.style.filter = 'brightness(1.1)';
            }
            
            const button = this.querySelector('.btn');
            if (button) {
                button.style.transform = 'translateY(-2px)';
                button.style.boxShadow = '0 6px 20px rgba(46, 111, 64, 0.3)';
            }
        });
        
        card.addEventListener('mouseleave', function(e) {
            hoverTimeout = setTimeout(() => {
                this.style.boxShadow = '';
                this.style.transform = '';
                
                const icon = this.querySelector('.path-icon, .tool-icon, .service-icon');
                if (icon) {
                    icon.style.transform = '';
                    icon.style.filter = '';
                }
                
                const button = this.querySelector('.btn');
                if (button) {
                    button.style.transform = '';
                    button.style.boxShadow = '';
                }
            }, 50);
        });
        
        // Add magnetic effect
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            
            const moveX = x * 0.1;
            const moveY = y * 0.1;
            
            this.style.transform = `translateY(-8px) scale(1.02) translate(${moveX}px, ${moveY}px)`;
        });
    });
}

function initCounterAnimations() {
    const counters = document.querySelectorAll('.trust-stat strong, .benefit-stat');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
                
                if (target > 0) {
                    animateCounter(counter, target);
                    counterObserver.unobserve(counter);
                }
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => counterObserver.observe(counter));
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 60; // 60 frames for ~1 second at 60fps
    const originalText = element.textContent;
    const suffix = originalText.replace(/[\d,]/g, '');
    
    function updateCounter() {
        current += increment;
        
        if (current < target) {
            element.textContent = Math.floor(current).toLocaleString() + suffix;
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target.toLocaleString() + suffix;
        }
    }
    
    updateCounter();
}

function initDynamicBackgrounds() {
    // Animated gradient backgrounds
    const sections = document.querySelectorAll('.hero, .audience-paths, .tools-preview');
    
    sections.forEach(section => {
        const colors = [
            'rgba(46, 111, 64, 0.05)',
            'rgba(46, 139, 87, 0.05)',
            'rgba(80, 200, 120, 0.05)',
            'rgba(212, 175, 55, 0.05)'
        ];
        
        let colorIndex = 0;
        
        function cycleBackground() {
            section.style.background = `linear-gradient(135deg, ${colors[colorIndex]}, ${colors[(colorIndex + 1) % colors.length]})`;
            colorIndex = (colorIndex + 1) % colors.length;
        }
        
        // Cycle background every 10 seconds
        setInterval(cycleBackground, 10000);
    });
    
    // Floating particles effect for hero
    createFloatingParticles();
}

function createFloatingParticles() {
    const hero = document.querySelector('.hero');
    if (!hero) return;
    
    const particleContainer = document.createElement('div');
    particleContainer.className = 'floating-particles';
    particleContainer.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1;
    `;
    
    hero.appendChild(particleContainer);
    
    // Create particles
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 4 + 2}px;
            height: ${Math.random() * 4 + 2}px;
            background: rgba(80, 200, 120, ${Math.random() * 0.3 + 0.1});
            border-radius: 50%;
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            animation: float ${Math.random() * 10 + 10}s infinite linear;
        `;
        
        particleContainer.appendChild(particle);
    }
    
    // Add particle animation CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes float {
            0% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) rotate(360deg);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

function initScrollEffects() {
    // Active navigation highlighting
    const sections = document.querySelectorAll('section[id], .hero, .contact-section, .investors-section');
    const navLinks = document.querySelectorAll('.nav a');
    
    window.addEventListener('scroll', function() {
        let current = '';
        const scrollPosition = window.pageYOffset + 200;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                current = section.getAttribute('id') || section.className.split(' ')[0].replace('-section', '');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            const linkTarget = link.getAttribute('href').substring(1);
            if (linkTarget === current || (linkTarget === 'home' && current === 'hero')) {
                link.classList.add('active');
            }
        });
    });
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatPhoneNumber(input) {
    const value = input.value.replace(/\D/g, '');
    if (value.length >= 10) {
        const formattedValue = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
        input.value = formattedValue;
    }
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length === 10;
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        clearFieldError(field);
        
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            // Additional validation
            if (field.type === 'email' && !validateEmail(field.value)) {
                showFieldError(field, 'Please enter a valid email address');
                isValid = false;
            }
            
            if (field.type === 'tel' && !validatePhone(field.value)) {
                showFieldError(field, 'Please enter a valid phone number');
                isValid = false;
            }
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    field.classList.add('error');
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('error');
    const errorMessage = field.parentNode.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#50C878' : type === 'error' ? '#dc3545' : '#2E6F40'};
        color: white;
        border-radius: 8px;
        z-index: 10000;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        max-width: 400px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

// FIXED scroll to section function with better element finding
function scrollToSection(sectionId) {
    let section = document.getElementById(sectionId);
    
    // If not found by ID, try by class
    if (!section) {
        section = document.querySelector(`.${sectionId}-section`);
    }
    
    // Handle special cases
    if (sectionId === 'home' && !section) {
        section = document.querySelector('.hero');
    } else if (sectionId === 'contact' && !section) {
        section = document.querySelector('.contact-section');
    } else if (sectionId === 'investors' && !section) {
        section = document.querySelector('.investors-section');
    }
    
    if (section) {
        const headerHeight = document.querySelector('.header').offsetHeight;
        const targetPosition = section.offsetTop - headerHeight - 10;
        
        window.scrollTo({
            top: Math.max(0, targetPosition),
            behavior: 'smooth'
        });
    }
}

async function storeLeadData(formData, estimatedValue) {
    const leadData = {
        propertyType: formData.get('propertyType'),
        location: formData.get('location'),
        size: formData.get('size'),
        currentUse: formData.get('currentUse'),
        timeline: formData.get('timeline'),
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        estimatedValue: estimatedValue
    };
    
    try {
        const response = await fetch('/api/property-valuation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(leadData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('Lead stored successfully:', result.leadId);
        } else {
            console.error('Failed to store lead:', result.message);
        }
    } catch (error) {
        console.error('Error storing lead data:', error);
        // Fallback to local storage
        localStorage.setItem('pendingLeads', JSON.stringify([
            ...(JSON.parse(localStorage.getItem('pendingLeads') || '[]')),
            { ...leadData, timestamp: new Date().toISOString(), type: 'property-valuation' }
        ]));
    }
}

async function storeContactData(formData) {
    const contactData = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        interest: formData.get('interest'),
        message: formData.get('message')
    };
    
    try {
        const response = await fetch('/api/contact', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(contactData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('Contact form submitted successfully:', result.leadId);
        } else {
            console.error('Failed to submit contact form:', result.message);
            showAlert('There was an error submitting your message. Please try again or call (713) 828-3701.', 'error');
        }
    } catch (error) {
        console.error('Error submitting contact form:', error);
        // Fallback to local storage
        localStorage.setItem('pendingLeads', JSON.stringify([
            ...(JSON.parse(localStorage.getItem('pendingLeads') || '[]')),
            { ...contactData, timestamp: new Date().toISOString(), type: 'contact-form' }
        ]));
        showAlert('Your message has been saved locally. Please try again or call (713) 828-3701.', 'warning');
    }
}

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
        if (e.target.classList.contains('path-card') || e.target.classList.contains('tool-card')) {
            e.preventDefault();
            e.target.click();
        }
    }
});

// Add CSS for active navigation links
const style = document.createElement('style');
style.textContent = `
    .nav a.active {
        color: var(--brand-primary) !important;
        background: rgba(46, 111, 64, 0.1) !important;
    }
    
    .alert {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);