/**
 * Jarvis - Futuristic UI Effects
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add futuristic hover effects for cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        // Create a subtle glow effect on hover
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 8px 30px rgba(0, 199, 254, 0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.08)';
        });
    });
    
    // Add pulse effect to Jarvis brand (if on homepage)
    const futuristicBrand = document.querySelector('.futuristic-brand');
    if (futuristicBrand && window.location.pathname === '/') {
        // Pulse effect for the brand every 5 seconds
        setInterval(() => {
            futuristicBrand.classList.add('pulse-effect');
            setTimeout(() => {
                futuristicBrand.classList.remove('pulse-effect');
            }, 1000);
        }, 5000);
    }
    
    // Add subtle transition effect for page load
    document.body.classList.add('fade-in');
    
    // Add glowing effect to buttons with class btn-glow
    const glowButtons = document.querySelectorAll('.btn-glow');
    glowButtons.forEach(button => {
        // Pulse the glow effect every 3 seconds
        setInterval(() => {
            button.classList.add('super-glow');
            setTimeout(() => {
                button.classList.remove('super-glow');
            }, 700);
        }, 3000);
    });
});

// Add CSS for the effects
document.head.insertAdjacentHTML('beforeend', `
<style>
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .cursor-effect {
        border-right: 2px solid transparent;
        animation: cursor-blink 1s step-end infinite;
    }
    
    @keyframes cursor-blink {
        from, to { border-color: transparent; }
        50% { border-color: var(--future-accent); }
    }
    
    .pulse-effect {
        animation: pulse 1s ease-in-out;
    }
    
    @keyframes pulse {
        0% { text-shadow: 0 0 10px var(--future-accent-glow), 0 0 20px var(--future-accent-glow); }
        50% { text-shadow: 0 0 20px var(--future-accent-glow), 0 0 40px var(--future-accent-glow); }
        100% { text-shadow: 0 0 10px var(--future-accent-glow), 0 0 20px var(--future-accent-glow); }
    }
    
    .super-glow {
        animation: superGlow 0.7s ease-in-out;
    }
    
    @keyframes superGlow {
        0% { box-shadow: 0 0 10px var(--future-accent-glow); }
        50% { box-shadow: 0 0 20px var(--future-accent-glow), 0 0 30px var(--future-accent-glow); }
        100% { box-shadow: 0 0 10px var(--future-accent-glow); }
    }
</style>
`);