"use client";

import { Mail } from "lucide-react";

export default function FooterSection() {

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer
      className="relative pt-8 pb-6 bg-storm-void overflow-hidden"
      aria-label="Footer"
    >
      {/* Top decorative border */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-parchment-gold/30 to-transparent" />

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-4xl px-4">
        {/* Logo centered */}
        <div className="flex flex-col items-center mb-4">
          <img
            src="/images/logo-m.png"
            alt="M"
            className="h-8 w-auto mb-2"
          />
          <span className="font-exocet text-lg text-storm-moon tracking-widest">
            Milo&apos;s Arcanum
          </span>
        </div>

        {/* Links section */}
        <div className="text-center mb-4">
          <p className="font-cinzel text-[10px] text-storm-moon/40 tracking-widest uppercase mb-3">
            Links to my other pages
          </p>
          
          {/* Social icons - horizontal */}
          <div className="flex items-center justify-center gap-6">
            {/* Instagram */}
            <a
              href="https://www.instagram.com/multimiloarts"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Instagram"
              className="flex items-center gap-2 text-storm-moon/60 hover:text-parchment-gold transition-all duration-300"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
                <circle cx="12" cy="12" r="5"/>
                <circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/>
              </svg>
              <span className="font-cinzel text-xs tracking-widest uppercase">Instagram</span>
            </a>
            
            {/* Discord */}
            <a
              href="https://discord.com/users/Milosaur"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Discord"
              className="flex items-center gap-2 text-storm-moon/60 hover:text-parchment-gold transition-all duration-300"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
              </svg>
              <span className="font-cinzel text-xs tracking-widest uppercase">Discord</span>
            </a>
            
            {/* Email */}
            <a
              href="mailto:MultiMilo@Proton.me"
              aria-label="Email"
              className="flex items-center gap-2 text-storm-moon/60 hover:text-parchment-gold transition-all duration-300"
            >
              <Mail className="w-4 h-4" />
              <span className="font-cinzel text-xs tracking-widest uppercase">Email</span>
            </a>
          </div>
        </div>

        {/* Return to top */}
        <button
          onClick={scrollToTop}
          className="group flex flex-col items-center gap-1 mx-auto mb-4 text-storm-moon/60 hover:text-parchment-gold transition-all duration-300"
          aria-label="Back to top"
        >
          <span className="font-cinzel text-[10px] tracking-widest uppercase">Return</span>
          <div className="w-8 h-8 flex items-center justify-center group-hover:-translate-y-1 transition-transform duration-300">
            <img
              src="/images/arrow-down.avif"
              alt="Scroll to top"
              className="w-5 h-5 rotate-180"
            />
          </div>
        </button>

        {/* Bottom divider */}
        <div className="relative w-32 h-3 mx-auto mb-4">
          <img
            src="/images/line-separator.avif"
            alt="Decorative divider"
            className="w-full h-full object-contain"
          />
        </div>

        {/* Copyright */}
        <div className="text-center">
          <p className="font-cormorant text-xs text-storm-moon/30 italic">
            &copy; 2026 Milo&apos;s Arcanum. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
