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
              href="#"
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
            
            {/* Twitter */}
            <a
              href="#"
              aria-label="Twitter"
              className="flex items-center gap-2 text-storm-moon/60 hover:text-parchment-gold transition-all duration-300"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
              <span className="font-cinzel text-xs tracking-widest uppercase">Twitter</span>
            </a>
            
            {/* Email */}
            <a
              href="mailto:hello@milosarcanum.com"
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
