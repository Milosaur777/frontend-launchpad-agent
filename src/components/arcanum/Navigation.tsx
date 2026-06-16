"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Scroll } from "lucide-react";

const navLinks = [
  { label: "About Me", mobileLabel: "About", href: "#about" },
  { label: "Gallery", href: "#gallery" },
  { label: "Contact", href: "#contact" },
];

export default function Navigation() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (href: string) => {
    const element = document.querySelector(href);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 1 }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 border-b ${
          isScrolled
            ? "bg-storm-void/40 backdrop-blur-xl border-parchment-gold/25 shadow-lg shadow-storm-void/20"
            : "bg-transparent border-storm-moon/5"
        }`}
      >
        <div className="mx-auto max-w-7xl px-3 md:px-8">
          <div className="flex h-10 md:h-12 items-center justify-between md:justify-center gap-2 md:gap-4">
            {/* Logo - always visible on all screens */}
            <button
              onClick={() => scrollToSection("#hero")}
              className="flex items-center gap-2 group shrink-0 mr-2"
            >
              <img
                src="/images/logo-m.png"
                alt="Milo's Arcanum"
                className="h-12 md:h-14 w-auto group-hover:drop-shadow-[0_0_8px_rgba(212,154,26,0.6)] transition-all duration-300"
              />
              <span className="font-exocet text-sm md:text-base font-bold tracking-widest hidden sm:block group-hover:text-glow-gold transition-all duration-300" style={{ color: '#c2ac7b' }}>
                Arcanum
              </span>
            </button>

            {/* Right side group: Nav Links + Hamburger */}
            <div className="flex items-center gap-4 md:gap-4 shrink-0">
              {/* Nav Links - all screens */}
              <nav className="flex items-center gap-4 md:gap-6 shrink-0">
                {/* Divider - desktop only */}
                <div className="hidden md:block w-px h-6 bg-storm-moon/20" />
                
                {navLinks.map((link) => (
                  <button
                    key={link.href}
                    onClick={() => scrollToSection(link.href)}
                    className="font-cinzel text-xs md:text-base font-bold text-storm-moon/80 hover:text-parchment-gold hover:text-glow-gold hover:drop-shadow-[0_0_8px_rgba(212,154,26,0.5)] transition-all duration-300 tracking-wider md:tracking-widest uppercase cursor-pointer whitespace-nowrap"
                  >
                    <span className="md:hidden">{link.mobileLabel || link.label}</span>
                    <span className="hidden md:inline">{link.label}</span>
                  </button>
                ))}
              </nav>

              {/* Mobile menu button */}
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="md:hidden shrink-0 w-8 h-8 rounded-lg bg-storm-mist/20 border border-parchment-gold/30 flex items-center justify-center text-parchment-gold hover:text-glow-gold hover:border-parchment-gold/60 hover:shadow-[0_0_10px_rgba(212,154,26,0.3)] transition-all duration-300"
                aria-label="Toggle menu"
              >
                {isMobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-40 bg-storm-void/95 backdrop-blur-md pt-20 px-6"
          >
            <nav className="flex flex-col gap-6">
              {navLinks.map((link, index) => (
                <motion.button
                  key={link.href}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  onClick={() => scrollToSection(link.href)}
                  className="flex items-center gap-4 py-4 border-b border-storm-cloud/20"
                >
                  <Scroll className="w-5 h-5 text-parchment-gold" />
                  <span className="font-cinzel text-lg font-bold text-storm-moon tracking-widest uppercase">
                    {link.label}
                  </span>
                </motion.button>
              ))}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
