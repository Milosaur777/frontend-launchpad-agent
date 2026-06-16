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
  height: string;
}

const artworks: ArtworkItem[] = [
  {
    id: 1,
    title: "The Storm-Crowned Castle",
    year: "2026",
    category: "Prints",
    etiquette: "Print",
    image: "/images/artwork-1.jpg",
    height: "h-64",
  },
  {
    id: 2,
    title: "Crimson Moon Ritual",
    year: "2025",
    category: "Originals",
    etiquette: "Original",
    image: "/images/artwork-2.jpg",
    height: "h-80",
  },
  {
    id: 3,
    title: "The Raven's Oath",
    year: "2026",
    category: "Stickers",
    etiquette: "Sticker",
    image: "/images/artwork-3.jpg",
    height: "h-56",
  },
  {
    id: 4,
    title: "Gothic Cathedral at Midnight",
    year: "2025",
    category: "Prints",
    etiquette: "Print",
    image: "/images/artwork-4.jpg",
    height: "h-72",
  },
  {
    id: 5,
    title: "The Illuminated Manuscript",
    year: "2026",
    category: "Pins",
    etiquette: "Pin",
    image: "/images/artwork-5.jpg",
    height: "h-60",
  },
  {
    id: 6,
    title: "Void Beyond the Stars",
    year: "2025",
    category: "Originals",
    etiquette: "Original",
    image: "/images/artwork-6.jpg",
    height: "h-96",
  },
  {
    id: 7,
    title: "The Wax Seal",
    year: "2026",
    category: "Pins",
    etiquette: "Pin",
    image: "/images/artwork-7.jpg",
    height: "h-52",
  },
  {
    id: 8,
    title: "Candlelit Scriptorium",
    year: "2025",
    category: "Stickers",
    etiquette: "Sticker",
    image: "/images/artwork-8.jpg",
    height: "h-72",
  },
];

const categories = ["All", "Prints", "Stickers", "Pins", "Originals"];

const etiquetteColors: Record<string, string> = {
  "Print": "bg-parchment-blue text-white",
  "Sticker": "bg-parchment-gold text-storm-void",
  "Pin": "bg-parchment-crimson text-white",
  "Original": "bg-void-purple text-white",
};

export default function GallerySection() {
  const [activeCategory, setActiveCategory] = useState("All");
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
          className="text-center mb-12"
        >
          <h2 className="font-exocet text-3xl md:text-4xl text-storm-moon mb-2 tracking-widest subtitle-pulse">
            The Reliquary
          </h2>
          <p className="font-cinzel text-sm text-storm-moon/60 tracking-widest uppercase mb-4">
            Gallery
          </p>
          <p className="font-cormorant text-lg text-storm-moon/60 italic max-w-lg mx-auto">
            Curated treasures from the Arcanum.
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
          className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6"
        >
          {filteredArtworks.map((artwork, index) => (
            <motion.div
              key={artwork.id}
              layout
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              className="break-inside-avoid"
            >
              <ArtworkCard artwork={artwork} />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function ArtworkCard({ artwork }: { artwork: ArtworkItem }) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="relative group cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Gothic Frame */}
      <div className="relative p-3 bg-gradient-to-b from-storm-mist/30 to-storm-void/60 rounded-lg border border-storm-cloud/20 transition-all duration-500 group-hover:border-parchment-gold/40 group-hover:shadow-2xl group-hover:shadow-parchment-gold/10">
        {/* Inner matting */}
        <div className="relative p-2 bg-parchment-cream/5 rounded">
          {/* Ornate frame corners */}
          <div className="absolute top-0 left-0 w-6 h-6 border-t-2 border-l-2 border-parchment-gold/40 rounded-tl" />
          <div className="absolute top-0 right-0 w-6 h-6 border-t-2 border-r-2 border-parchment-gold/40 rounded-tr" />
          <div className="absolute bottom-0 left-0 w-6 h-6 border-b-2 border-l-2 border-parchment-gold/40 rounded-bl" />
          <div className="absolute bottom-0 right-0 w-6 h-6 border-b-2 border-r-2 border-parchment-gold/40 rounded-br" />

          {/* Artwork placeholder */}
          <div className={`relative ${artwork.height} w-full bg-storm-mist/20 rounded overflow-hidden`}>
            {/* Placeholder gradient pattern */}
            <div className="absolute inset-0 bg-gradient-to-br from-storm-mist/30 via-storm-cloud/20 to-storm-void/40" />
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="font-cinzel text-storm-moon/20 text-sm">{artwork.title}</span>
            </div>
            
            {/* Hover overlay */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-t from-storm-void/80 via-transparent to-transparent flex items-end justify-center pb-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: isHovered ? 1 : 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="text-center">
                <p className="font-cinzel text-sm text-storm-moon">{artwork.title}</p>
                <p className="font-cormorant text-xs text-storm-moon/60">{artwork.year}</p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Etiquette label */}
      <motion.div
        className="absolute -bottom-3 left-1/2 -translate-x-1/2 z-10"
        initial={{ y: 10, opacity: 0 }}
        animate={{ y: isHovered ? 0 : 10, opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className={`px-3 py-1 rounded-full font-cinzel text-xs tracking-wider ${etiquetteColors[artwork.etiquette]}`}>
          <span className="flex items-center gap-1.5">
            {/* Mini wax seal icon */}
            <svg className="w-3 h-3" viewBox="0 0 12 12" fill="currentColor">
              <circle cx="6" cy="6" r="5" />
              <circle cx="6" cy="6" r="2" fill="none" stroke="currentColor" strokeWidth="0.5" />
            </svg>
            {artwork.etiquette}
          </span>
        </div>
      </motion.div>
    </div>
  );
}
