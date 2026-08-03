"use client";

import { useState, useRef } from "react";
import { motion, useInView } from "framer-motion";
import Image from "next/image";

interface ArtworkItem {
  id: number;
  title: string;
  year: string;
  category: string;
  etiquette: string;
  image: string;
  materials: string;
  thoughts: string;
  link?: string;
}

const artworks: ArtworkItem[] = [
  {
    id: 1,
    title: "Hex Lasher",
    year: "2023",
    category: "Sketches",
    etiquette: "Sketch",
    image: "/images/sketches/witchfighter.avif",
    materials: "ArtRage Vitae (digital, pencil simulation)",
    thoughts: "A love letter to fighting games. She is a zoner who hovers above the battlefield, wielding a laser whip and weaving spells before opponents can get within striking range. Fighting game animation is what made me fall in love with drawing.",
  },
  {
    id: 2,
    title: "Ophanim's Radiance",
    year: "2023",
    category: "Sketches",
    etiquette: "Sketch",
    image: "/images/sketches/biblicallyaccurrateangel.avif",
    materials: "ArtRage Vitae (digital, pencil simulation)",
    thoughts: "Ezekiel's vision, wheels within wheels, eyes upon eyes.",
  },
  {
    id: 3,
    title: "Cyberpunk Ninja",
    year: "2023",
    category: "Sketches",
    etiquette: "Sketch",
    image: "/images/sketches/cyberpunkz_12_11_23.avif",
    materials: "ArtRage Vitae (digital, pencil simulation)",
    thoughts: "A agile looking bounty hunter. He is part of a lethal crew that specialize in quick extractions.",
  },
  {
    id: 4,
    title: "The Little Night",
    year: "2023",
    category: "Sketches",
    etiquette: "Sketch",
    image: "/images/sketches/cutevampire_stylized.avif",
    materials: "ArtRage Vitae (digital, pencil simulation)",
    thoughts: "Halloween pin-up with fangs.",
  },
  {
    id: 5,
    title: "Starlet Gaze",
    year: "2023",
    category: "Sketches",
    etiquette: "Sketch",
    image: "/images/sketches/moviestar.avif",
    materials: "ArtRage Vitae (digital, pencil simulation)",
    thoughts: "I wanted to make a movie poster like sketch. Her eyes are hungry and scheming.",
  },
  {
    id: 6,
    title: "Fallen Vanguard",
    year: "2023",
    category: "Sketches",
    etiquette: "Sketch",
    image: "/images/sketches/androgenous_angel.avif",
    materials: "ArtRage Vitae (digital, pencil simulation)",
    thoughts: "Neither man nor woman, I set out to draw the most androgynous figure I could.",
  },
  {
    id: 7,
    title: "Welcome to AVAX",
    year: "2026",
    category: "Websites",
    etiquette: "Website",
    image: "/images/webpages/welcome-to-avax.avif",
    materials: "OpenCode - Kimi K3",
    thoughts: "Crypto project. Scans your crypto wallet for NFTs that allow you to buy a certain amount of a meme coin.",
    link: "https://welcometoavax.vercel.app",
  },
  {
    id: 8,
    title: "Unhinged RP",
    year: "2026",
    category: "Websites",
    etiquette: "Website",
    image: "/images/webpages/unhinged-rp.avif",
    materials: "OpenCode - Kimi K3, Supabase and N8N integration",
    thoughts: "Dating platform for people with role-playing and original characters. Create your character, swipe on other people's characters, and find a match to communicate over an encrypted chat.",
    link: "https://unhinged-rp.vercel.app",
  },
];

const categories = ["All", "Sketches", "Websites"];

const etiquetteColors: Record<string, string> = {
  "Sketch": "bg-parchment-crimson text-white",
  "Website": "bg-parchment-blue text-white",
};

export default function GallerySection() {
  const [activeCategory, setActiveCategory] = useState("All");
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  const filteredArtworks = activeCategory === "All" 
    ? artworks 
    : artworks.filter(art => art.category === activeCategory);

  return (
    <section
      ref={ref}
      className="relative py-24 md:py-32 overflow-hidden"
      aria-label="Gallery section - Artwork collection"
    >

      <div className="relative z-10 mx-auto max-w-7xl px-4 md:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 rounded-full bg-storm-void px-4 py-2 border border-parchment-gold/30 mb-6">
            <span className="text-sm font-semibold text-storm-moon">Collection</span>
          </div>
          <h2 className="font-exocet text-4xl md:text-5xl text-storm-moon mb-4 subtitle-pulse">
            The Reliquary
          </h2>
          <div className="relative w-48 md:w-64 h-6 mx-auto mb-4">
            <img
              src="/images/line-separator.avif"
              alt="Decorative divider"
              className="w-full h-full object-contain"
            />
          </div>
          <p className="font-cormorant text-lg text-storm-moon/70 max-w-xl mx-auto">
            Late-night marks on paper and screen.
          </p>
        </motion.div>

        {/* Category Filters - Styled as wax seals */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex flex-wrap justify-center gap-3 mb-12"
        >
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`relative px-5 py-2 rounded-full font-cinzel text-sm tracking-wider transition-all duration-300 ${
                activeCategory === category
                  ? "bg-parchment-crimson text-white shadow-lg shadow-parchment-crimson/20 scale-105"
                  : "bg-storm-mist/20 text-storm-moon/70 hover:bg-storm-mist/40 hover:text-storm-moon"
              }`}
              aria-label={`Filter by ${category}`}
            >
              {/* Wax seal texture */}
              <span className="absolute inset-0 rounded-full opacity-10" style={{
                backgroundImage: `radial-gradient(circle at 30% 30%, rgba(255,255,255,0.3) 0%, transparent 60%)`
              }} />
              {category}
            </button>
          ))}
        </motion.div>

        {/* Masonry Grid */}
        <motion.div
          layout
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredArtworks.map((artwork, index) => (
            <motion.div
              key={artwork.id}
              layout
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.1 }}
            >
              <ArtworkCard 
                artwork={artwork} 
                isExpanded={expandedId === artwork.id}
                onToggle={() => setExpandedId(expandedId === artwork.id ? null : artwork.id)}
              />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function ArtworkCard({ artwork, isExpanded, onToggle }: { artwork: ArtworkItem; isExpanded: boolean; onToggle: () => void }) {
  const [imgLoaded, setImgLoaded] = useState(false);

  return (
    <div className="relative group">
      {/* Gothic Frame around image */}
      <div className={`relative p-3 bg-gradient-to-b from-storm-mist/30 to-storm-void/60 rounded-lg border transition-all duration-500 ${
        isExpanded 
          ? "border-parchment-gold/50 shadow-2xl shadow-parchment-gold/15" 
          : "border-storm-cloud/20 group-hover:border-parchment-gold/40 group-hover:shadow-2xl group-hover:shadow-parchment-gold/10"
      }`}>
        {/* Inner matting */}
        <div className="relative p-2 bg-parchment-cream/5 rounded">
          {/* Ornate frame corners */}
          <div className="absolute top-0 left-0 w-6 h-6 border-t-2 border-l-2 border-parchment-gold/40 rounded-tl" />
          <div className="absolute top-0 right-0 w-6 h-6 border-t-2 border-r-2 border-parchment-gold/40 rounded-tr" />
          <div className="absolute bottom-0 left-0 w-6 h-6 border-b-2 border-l-2 border-parchment-gold/40 rounded-bl" />
          <div className="absolute bottom-0 right-0 w-6 h-6 border-b-2 border-r-2 border-parchment-gold/40 rounded-br" />

          {/* Artwork Image - clickable */}
          <div 
            className="relative w-full bg-storm-mist/20 rounded overflow-hidden cursor-pointer"
            onClick={onToggle}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') onToggle(); }}
            aria-expanded={isExpanded}
            aria-label={`${isExpanded ? "Collapse" : "Expand"} details for ${artwork.title}`}
          >
            {!imgLoaded && (
              <div className="w-full aspect-[4/3] bg-gradient-to-br from-storm-mist/30 via-storm-cloud/20 to-storm-void/40 animate-pulse" />
            )}
            <Image
              src={artwork.image}
              alt={artwork.title}
              width={800}
              height={600}
              className={`w-full h-auto transition-opacity duration-500 ${imgLoaded ? "opacity-100" : "opacity-0"}`}
              onLoad={() => setImgLoaded(true)}
            />

            {/* Etiquette badge */}
            <div className="absolute top-3 right-3 z-10">
              <div className={`px-2.5 py-1 rounded-full font-cinzel text-[10px] tracking-wider shadow-lg ${etiquetteColors[artwork.etiquette]}`}>
                <span className="flex items-center gap-1">
                  <svg className="w-2.5 h-2.5" viewBox="0 0 12 12" fill="currentColor">
                    <circle cx="6" cy="6" r="5" />
                    <circle cx="6" cy="6" r="2" fill="none" stroke="currentColor" strokeWidth="0.5" />
                  </svg>
                  {artwork.etiquette}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Description section beneath the frame */}
      <div className="mt-4 px-1 space-y-2">
        {/* Title + Arrow */}
        <div className="flex items-center justify-between gap-3">
          <h3 className="font-cinzel text-base md:text-lg text-storm-moon tracking-wide leading-tight">
            {artwork.title}
          </h3>
          <img
            src="/images/arrow-down.avif"
            alt={isExpanded ? "Collapse details" : "Expand details"}
            className={`w-4 h-4 transition-transform duration-300 ${isExpanded ? "rotate-180" : ""}`}
          />
        </div>

        {/* Expandable Details */}
        <div 
          className={`overflow-hidden transition-all duration-300 ease-out ${
            isExpanded ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
          }`}
        >
          <div className="pt-2 space-y-2">
            {/* Materials */}
            <p className="font-cormorant text-sm text-parchment-gold/70 italic leading-snug">
              <span className="text-parchment-gold/50 text-[10px] uppercase tracking-wider font-cinzel not-italic mr-1.5">Media</span>
              {artwork.materials}
            </p>

            {/* Divider */}
            <div className="w-8 h-px bg-gradient-to-r from-parchment-gold/40 to-transparent" />

            {/* Thoughts */}
            <p className="font-cormorant text-sm text-storm-moon/60 leading-relaxed">
              {artwork.thoughts}
            </p>

            {/* External link */}
            {artwork.link && (
              <a
                href={artwork.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 font-cinzel text-xs text-parchment-gold hover:text-parchment-gold/80 hover:underline tracking-wider uppercase transition-colors mt-1 cursor-pointer"
              >
                {artwork.link.replace(/^https?:\/\//, "")}
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
