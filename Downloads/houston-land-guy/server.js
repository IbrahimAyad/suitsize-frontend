const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('.'));

// Database setup
const dbPath = path.join(__dirname, 'leads.db');
const db = new sqlite3.Database(dbPath);

// Initialize database tables
db.serialize(() => {
    // Property valuation leads table
    db.run(`CREATE TABLE IF NOT EXISTS property_valuations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_type TEXT NOT NULL,
        location TEXT NOT NULL,
        size REAL NOT NULL,
        current_use TEXT NOT NULL,
        timeline TEXT NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        estimated_value INTEGER,
        lead_source TEXT DEFAULT 'website',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new',
        notes TEXT
    )`);
    
    // Contact form submissions table
    db.run(`CREATE TABLE IF NOT EXISTS contact_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        interest TEXT NOT NULL,
        message TEXT,
        lead_source TEXT DEFAULT 'contact_form',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new',
        notes TEXT
    )`);
    
    // ROI calculations table
    db.run(`CREATE TABLE IF NOT EXISTS roi_calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        land_cost REAL NOT NULL,
        development_cost REAL NOT NULL,
        projected_sale_price REAL NOT NULL,
        timeline TEXT NOT NULL,
        total_investment REAL,
        projected_profit REAL,
        roi_percentage REAL,
        annualized_return REAL,
        ip_address TEXT,
        user_agent TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
    
    // Investment calculations table
    db.run(`CREATE TABLE IF NOT EXISTS investment_calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        investment_amount REAL NOT NULL,
        return_rate REAL NOT NULL,
        timeline INTEGER NOT NULL,
        projected_value REAL,
        total_return REAL,
        annual_return REAL,
        ip_address TEXT,
        user_agent TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
    
    // Analytics events table
    db.run(`CREATE TABLE IF NOT EXISTS analytics_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        event_category TEXT,
        event_label TEXT,
        event_value REAL,
        user_id TEXT,
        session_id TEXT,
        ip_address TEXT,
        user_agent TEXT,
        page_url TEXT,
        referrer TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
});

// Email configuration
const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: process.env.SMTP_PORT || 587,
    secure: false,
    auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS
    }
});

// Utility functions
function getClientIP(req) {
    return req.ip || req.connection.remoteAddress || req.socket.remoteAddress || 
           (req.connection.socket ? req.connection.socket.remoteAddress : null);
}

function sanitizeInput(input) {
    if (typeof input !== 'string') return input;
    return input.trim().replace(/[<>]/g, '');
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePhone(phone) {
    const phoneRegex = /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;
    return phoneRegex.test(phone);
}

// API Routes

// Property Valuation Endpoint
app.post('/api/property-valuation', async (req, res) => {
    try {
        const {
            propertyType,
            location,
            size,
            currentUse,
            timeline,
            name,
            email,
            phone,
            estimatedValue
        } = req.body;
        
        // Validate required fields
        if (!propertyType || !location || !size || !currentUse || !timeline || !name || !email || !phone) {
            return res.status(400).json({
                success: false,
                message: 'All fields are required'
            });
        }
        
        // Validate email and phone
        if (!validateEmail(email)) {
            return res.status(400).json({
                success: false,
                message: 'Invalid email address'
            });
        }
        
        if (!validatePhone(phone)) {
            return res.status(400).json({
                success: false,
                message: 'Invalid phone number'
            });
        }
        
        // Sanitize inputs
        const sanitizedData = {
            propertyType: sanitizeInput(propertyType),
            location: sanitizeInput(location),
            size: parseFloat(size),
            currentUse: sanitizeInput(currentUse),
            timeline: sanitizeInput(timeline),
            name: sanitizeInput(name),
            email: sanitizeInput(email),
            phone: sanitizeInput(phone),
            estimatedValue: parseInt(estimatedValue) || 0
        };
        
        // Insert into database
        const sql = `INSERT INTO property_valuations 
                    (property_type, location, size, current_use, timeline, name, email, phone, estimated_value)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`;
        
        db.run(sql, [
            sanitizedData.propertyType,
            sanitizedData.location,
            sanitizedData.size,
            sanitizedData.currentUse,
            sanitizedData.timeline,
            sanitizedData.name,
            sanitizedData.email,
            sanitizedData.phone,
            sanitizedData.estimatedValue
        ], function(err) {
            if (err) {
                console.error('Database error:', err);
                return res.status(500).json({
                    success: false,
                    message: 'Database error'
                });
            }
            
            // Send notification email
            sendPropertyValuationNotification(sanitizedData, this.lastID);
            
            res.json({
                success: true,
                message: 'Property valuation request submitted successfully',
                leadId: this.lastID
            });
        });
        
    } catch (error) {
        console.error('Property valuation error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Contact Form Endpoint
app.post('/api/contact', async (req, res) => {
    try {
        const { name, email, phone, interest, message } = req.body;
        
        // Validate required fields
        if (!name || !email || !phone || !interest) {
            return res.status(400).json({
                success: false,
                message: 'Name, email, phone, and interest are required'
            });
        }
        
        // Validate email and phone
        if (!validateEmail(email)) {
            return res.status(400).json({
                success: false,
                message: 'Invalid email address'
            });
        }
        
        if (!validatePhone(phone)) {
            return res.status(400).json({
                success: false,
                message: 'Invalid phone number'
            });
        }
        
        // Sanitize inputs
        const sanitizedData = {
            name: sanitizeInput(name),
            email: sanitizeInput(email),
            phone: sanitizeInput(phone),
            interest: sanitizeInput(interest),
            message: sanitizeInput(message || '')
        };
        
        // Insert into database
        const sql = `INSERT INTO contact_submissions (name, email, phone, interest, message)
                    VALUES (?, ?, ?, ?, ?)`;
        
        db.run(sql, [
            sanitizedData.name,
            sanitizedData.email,
            sanitizedData.phone,
            sanitizedData.interest,
            sanitizedData.message
        ], function(err) {
            if (err) {
                console.error('Database error:', err);
                return res.status(500).json({
                    success: false,
                    message: 'Database error'
                });
            }
            
            // Send notification email
            sendContactNotification(sanitizedData, this.lastID);
            
            res.json({
                success: true,
                message: 'Contact form submitted successfully',
                leadId: this.lastID
            });
        });
        
    } catch (error) {
        console.error('Contact form error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// ROI Calculator Endpoint
app.post('/api/roi-calculation', async (req, res) => {
    try {
        const { landCost, developmentCost, projectedSalePrice, timeline } = req.body;
        
        if (!landCost || !developmentCost || !projectedSalePrice || !timeline) {
            return res.status(400).json({
                success: false,
                message: 'All calculation fields are required'
            });
        }
        
        const totalInvestment = parseFloat(landCost) + parseFloat(developmentCost);
        const projectedProfit = parseFloat(projectedSalePrice) - totalInvestment;
        const roiPercentage = (projectedProfit / totalInvestment) * 100;
        
        const timelineYears = {
            '6 months': 0.5,
            '1 year': 1,
            '18 months': 1.5,
            '2 years': 2,
            '3+ years': 3
        };
        
        const years = timelineYears[timeline] || 1;
        const annualizedReturn = roiPercentage / years;
        
        // Store calculation
        const sql = `INSERT INTO roi_calculations 
                    (land_cost, development_cost, projected_sale_price, timeline, 
                     total_investment, projected_profit, roi_percentage, annualized_return,
                     ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`;
        
        db.run(sql, [
            parseFloat(landCost),
            parseFloat(developmentCost),
            parseFloat(projectedSalePrice),
            timeline,
            totalInvestment,
            projectedProfit,
            roiPercentage,
            annualizedReturn,
            getClientIP(req),
            req.get('User-Agent')
        ], function(err) {
            if (err) {
                console.error('Database error:', err);
            }
        });
        
        res.json({
            success: true,
            results: {
                totalInvestment,
                projectedProfit,
                roiPercentage: parseFloat(roiPercentage.toFixed(1)),
                annualizedReturn: parseFloat(annualizedReturn.toFixed(1))
            }
        });
        
    } catch (error) {
        console.error('ROI calculation error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Investment Calculator Endpoint
app.post('/api/investment-calculation', async (req, res) => {
    try {
        const { investmentAmount, returnRate, timeline } = req.body;
        
        if (!investmentAmount || !returnRate || !timeline) {
            return res.status(400).json({
                success: false,
                message: 'All calculation fields are required'
            });
        }
        
        const amount = parseFloat(investmentAmount);
        const rate = parseFloat(returnRate) / 100;
        const years = parseInt(timeline);
        
        const projectedValue = amount * Math.pow(1 + rate, years);
        const totalReturn = projectedValue - amount;
        const annualReturn = totalReturn / years;
        
        // Store calculation
        const sql = `INSERT INTO investment_calculations 
                    (investment_amount, return_rate, timeline, projected_value, 
                     total_return, annual_return, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;
        
        db.run(sql, [
            amount,
            parseFloat(returnRate),
            years,
            projectedValue,
            totalReturn,
            annualReturn,
            getClientIP(req),
            req.get('User-Agent')
        ], function(err) {
            if (err) {
                console.error('Database error:', err);
            }
        });
        
        res.json({
            success: true,
            results: {
                initialInvestment: amount,
                projectedValue: Math.round(projectedValue),
                totalReturn: Math.round(totalReturn),
                annualReturn: Math.round(annualReturn)
            }
        });
        
    } catch (error) {
        console.error('Investment calculation error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Analytics Event Tracking Endpoint
app.post('/api/analytics/event', async (req, res) => {
    try {
        const {
            eventName,
            eventCategory,
            eventLabel,
            eventValue,
            userId,
            sessionId,
            pageUrl,
            referrer
        } = req.body;
        
        if (!eventName) {
            return res.status(400).json({
                success: false,
                message: 'Event name is required'
            });
        }
        
        const sql = `INSERT INTO analytics_events 
                    (event_name, event_category, event_label, event_value, 
                     user_id, session_id, ip_address, user_agent, page_url, referrer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`;
        
        db.run(sql, [
            eventName,
            eventCategory || null,
            eventLabel || null,
            eventValue || null,
            userId || null,
            sessionId || null,
            getClientIP(req),
            req.get('User-Agent'),
            pageUrl || null,
            referrer || null
        ], function(err) {
            if (err) {
                console.error('Analytics tracking error:', err);
                return res.status(500).json({
                    success: false,
                    message: 'Failed to track event'
                });
            }
            
            res.json({
                success: true,
                message: 'Event tracked successfully'
            });
        });
        
    } catch (error) {
        console.error('Analytics event error:', error);
        res.status(500).json({
            success: false,
            message: 'Internal server error'
        });
    }
});

// Lead Management Endpoints (for admin dashboard)
app.get('/api/admin/leads', (req, res) => {
    const { type, status, limit = 100 } = req.query;
    
    let sql;
    let params = [];
    
    switch(type) {
        case 'property':
            sql = `SELECT * FROM property_valuations`;
            if (status) {
                sql += ` WHERE status = ?`;
                params.push(status);
            }
            sql += ` ORDER BY created_at DESC LIMIT ?`;
            params.push(parseInt(limit));
            break;
        case 'contact':
            sql = `SELECT * FROM contact_submissions`;
            if (status) {
                sql += ` WHERE status = ?`;
                params.push(status);
            }
            sql += ` ORDER BY created_at DESC LIMIT ?`;
            params.push(parseInt(limit));
            break;
        default:
            return res.status(400).json({
                success: false,
                message: 'Invalid lead type'
            });
    }
    
    db.all(sql, params, (err, rows) => {
        if (err) {
            console.error('Database error:', err);
            return res.status(500).json({
                success: false,
                message: 'Database error'
            });
        }
        
        res.json({
            success: true,
            leads: rows
        });
    });
});

// Email notification functions
async function sendPropertyValuationNotification(data, leadId) {
    try {
        const mailOptions = {
            from: process.env.SMTP_USER,
            to: process.env.NOTIFICATION_EMAIL || 'info@houstonlandguy.com',
            subject: `New Property Valuation Request - Lead #${leadId}`,
            html: `
                <h2>New Property Valuation Request</h2>
                <p><strong>Lead ID:</strong> ${leadId}</p>
                <p><strong>Name:</strong> ${data.name}</p>
                <p><strong>Email:</strong> ${data.email}</p>
                <p><strong>Phone:</strong> ${data.phone}</p>
                <p><strong>Property Type:</strong> ${data.propertyType}</p>
                <p><strong>Location:</strong> ${data.location}</p>
                <p><strong>Size:</strong> ${data.size} acres</p>
                <p><strong>Current Use:</strong> ${data.currentUse}</p>
                <p><strong>Timeline:</strong> ${data.timeline}</p>
                <p><strong>Estimated Value:</strong> $${data.estimatedValue.toLocaleString()}</p>
                
                <h3>Next Steps:</h3>
                <ul>
                    <li>Call within 24 hours: ${data.phone}</li>
                    <li>Send detailed market analysis</li>
                    <li>Schedule property consultation</li>
                </ul>
            `
        };
        
        await transporter.sendMail(mailOptions);
        console.log('Property valuation notification sent');
    } catch (error) {
        console.error('Failed to send property valuation notification:', error);
    }
}

async function sendContactNotification(data, leadId) {
    try {
        const mailOptions = {
            from: process.env.SMTP_USER,
            to: process.env.NOTIFICATION_EMAIL || 'info@houstonlandguy.com',
            subject: `New Contact Form Submission - Lead #${leadId}`,
            html: `
                <h2>New Contact Form Submission</h2>
                <p><strong>Lead ID:</strong> ${leadId}</p>
                <p><strong>Name:</strong> ${data.name}</p>
                <p><strong>Email:</strong> ${data.email}</p>
                <p><strong>Phone:</strong> ${data.phone}</p>
                <p><strong>Interest:</strong> ${data.interest}</p>
                <p><strong>Message:</strong></p>
                <blockquote>${data.message}</blockquote>
                
                <h3>Next Steps:</h3>
                <ul>
                    <li>Call within 24 hours: ${data.phone}</li>
                    <li>Follow up via email</li>
                    <li>Send relevant information based on interest</li>
                </ul>
            `
        };
        
        await transporter.sendMail(mailOptions);
        console.log('Contact form notification sent');
    } catch (error) {
        console.error('Failed to send contact notification:', error);
    }
}

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        success: true,
        message: 'Houston Land Guy API is running',
        timestamp: new Date().toISOString()
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        success: false,
        message: 'Something went wrong!'
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Houston Land Guy server running on port ${PORT}`);
    console.log(`Visit: http://localhost:${PORT}`);
});

module.exports = app; 