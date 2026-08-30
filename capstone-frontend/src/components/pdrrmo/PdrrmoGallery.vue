<template>
  <div class="pdrrmo-gallery-wrap">
    <div v-if="categories.length > 1" class="gallery-filters">
      <button
        v-for="cat in categories"
        :key="cat"
        type="button"
        class="gallery-filter"
        :class="{ active: activeCategory === cat }"
        @click="setCategory(cat)"
      >
        {{ cat }}
      </button>
    </div>

    <div
      class="pdrrmo-gallery"
      @mouseenter="pause"
      @mouseleave="resume"
      @pointerdown="onPointerDown"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <div class="gallery-frame">
        <div
          v-for="(slide, index) in filteredSlides"
          :key="slide.id ?? index"
          class="gallery-slide"
          :class="{ active: index === activeIndex }"
        >
          <img
            v-if="slide.image && !slide.failed"
            :src="slide.image"
            :alt="slide.title"
            class="slide-img"
            @error="onImageError(slide)"
          />
          <div v-else class="slide-fallback">
            <span class="fallback-icon">📷</span>
            <span class="fallback-text">Add photo</span>
          </div>

          <div class="slide-overlay"></div>

          <div class="slide-caption">
            <span v-if="slide.category" class="slide-category">{{ slide.category }}</span>
            <span v-if="slide.year" class="slide-year">{{ slide.year }}</span>
            <h4>{{ slide.title }}</h4>
            <p v-if="slide.description">{{ slide.description }}</p>
          </div>
        </div>

        <div v-if="filteredSlides.length === 0" class="gallery-empty">
          <span class="fallback-icon">📷</span>
          <p>No photos in this category yet.</p>
        </div>
      </div>

      <template v-if="filteredSlides.length > 1">
        <button class="gallery-nav prev" type="button" @click="prevSlide" aria-label="Previous photo">
          ‹
        </button>
        <button class="gallery-nav next" type="button" @click="nextSlide" aria-label="Next photo">
          ›
        </button>

        <div class="gallery-dots">
          <button
            v-for="(slide, index) in filteredSlides"
            :key="'dot-' + (slide.id ?? index)"
            type="button"
            class="gallery-dot"
            :class="{ active: index === activeIndex }"
            :aria-label="`Go to photo ${index + 1}`"
            @click="goToSlide(index)"
          ></button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

const props = defineProps({
  // Each slide: { id, image, title, description, year, category }
  // `image` can be left blank/undefined until real photos are added —
  // the component shows a clean placeholder instead of a broken image icon.
  // `category` groups slides under filter buttons (e.g. "Training", "Operations", "Meetings").
  // Leave category unset (or use the same value for every slide) to hide the filter bar.
  slides: {
    type: Array,
    required: true,
  },
  autoplayInterval: {
    type: Number,
    default: 4500,
  },
})

// local reactive copy so we can flag failed image loads without mutating props
const slides = reactive(props.slides.map((s) => ({ ...s, failed: !s.image })))

const categories = computed(() => {
  const found = [...new Set(slides.map((s) => s.category).filter(Boolean))]
  return found.length > 1 ? ['All', ...found] : []
})

const activeCategory = ref('All')
const setCategory = (cat) => {
  activeCategory.value = cat
  activeIndex.value = 0
}

const filteredSlides = computed(() => {
  if (activeCategory.value === 'All' || categories.value.length === 0) return slides
  return slides.filter((s) => s.category === activeCategory.value)
})

const activeIndex = ref(0)
let timer = null
let dragStartX = 0
let dragging = false

const nextSlide = () => {
  if (filteredSlides.value.length === 0) return
  activeIndex.value = (activeIndex.value + 1) % filteredSlides.value.length
}
const prevSlide = () => {
  if (filteredSlides.value.length === 0) return
  activeIndex.value = (activeIndex.value - 1 + filteredSlides.value.length) % filteredSlides.value.length
}
const goToSlide = (index) => {
  activeIndex.value = index
}

const start = () => {
  stop()
  if (filteredSlides.value.length > 1) {
    timer = setInterval(nextSlide, props.autoplayInterval)
  }
}
const stop = () => {
  if (timer) clearInterval(timer)
  timer = null
}
const pause = () => stop()
const resume = () => start()

// restart autoplay whenever the visible slide set changes (e.g. filter switched)
watch(filteredSlides, () => start())

const onImageError = (slide) => {
  slide.failed = true
}

// simple swipe support for touch/mouse drag
const onPointerDown = (event) => {
  dragging = true
  dragStartX = event.clientX
  stop()
}
const onPointerUp = (event) => {
  if (!dragging) return
  const delta = event.clientX - dragStartX
  const threshold = 40

  if (delta > threshold) prevSlide()
  else if (delta < -threshold) nextSlide()

  dragging = false
  start()
}

onMounted(start)
onBeforeUnmount(stop)
</script>

<style scoped>
.pdrrmo-gallery-wrap {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.gallery-filters {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.6rem;
}

.gallery-filter {
  border: 1px solid var(--sr-border-accent, rgba(96, 165, 250, 0.16));
  background: var(--sr-chip-bg, rgba(11, 24, 48, 0.72));
  color: var(--sr-text-muted, #9cb3ce);
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.gallery-filter:hover {
  transform: translateY(-1px);
}

.gallery-filter.active {
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  color: #ffffff;
  border-color: transparent;
}

.gallery-empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  color: var(--sr-text-faint, #8ea7c3);
}

.gallery-empty p {
  margin: 0;
  font-weight: 600;
}

.pdrrmo-gallery {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 8;
  border-radius: 26px;
  overflow: hidden;
  border: 1px solid var(--sr-border-soft, rgba(148, 163, 184, 0.1));
  box-shadow: 0 24px 48px var(--sr-shadow-med, rgba(0, 0, 0, 0.24));
  touch-action: pan-y;
  cursor: grab;
  background: var(--sr-card-bg, rgba(9, 18, 34, 0.84));
}

.pdrrmo-gallery:active {
  cursor: grabbing;
}

.gallery-frame {
  position: relative;
  width: 100%;
  height: 100%;
}

.gallery-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.9s ease;
}

.gallery-slide.active {
  opacity: 1;
  visibility: visible;
  z-index: 1;
}

.slide-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transform: scale(1.02);
  animation: kenburns 9s ease-in-out infinite alternate;
}

.gallery-slide.active .slide-img {
  animation-play-state: running;
}

.gallery-slide:not(.active) .slide-img {
  animation-play-state: paused;
}

@keyframes kenburns {
  from {
    transform: scale(1) translate(0, 0);
  }
  to {
    transform: scale(1.12) translate(-1.5%, -1.5%);
  }
}

.slide-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--sr-text-faint, #8ea7c3);
  background:
    repeating-linear-gradient(
      135deg,
      rgba(148, 163, 184, 0.06) 0px,
      rgba(148, 163, 184, 0.06) 10px,
      transparent 10px,
      transparent 20px
    );
}

.fallback-icon {
  font-size: 2.2rem;
}

.fallback-text {
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.slide-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(0, 0, 0, 0.72) 100%);
  pointer-events: none;
}

.slide-caption {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 1.4rem 1.6rem;
  color: #f8fbff;
}

.slide-year {
  display: inline-flex;
  padding: 0.25rem 0.6rem;
  margin-bottom: 0.5rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  background: rgba(37, 99, 235, 0.35);
  border: 1px solid rgba(147, 197, 253, 0.4);
}

.slide-category {
  display: inline-flex;
  padding: 0.25rem 0.6rem;
  margin-bottom: 0.5rem;
  margin-right: 0.4rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  background: rgba(249, 115, 22, 0.35);
  border: 1px solid rgba(253, 186, 116, 0.4);
}

.slide-caption h4 {
  margin: 0 0 0.25rem;
  font-size: 1.2rem;
}

.slide-caption p {
  margin: 0;
  font-size: 0.88rem;
  color: rgba(248, 251, 255, 0.82);
  max-width: 56ch;
}

.gallery-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 2;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.28);
  background: rgba(9, 18, 34, 0.45);
  color: #fff;
  font-size: 1.4rem;
  line-height: 1;
  cursor: pointer;
  backdrop-filter: blur(6px);
  transition: background 0.2s ease, transform 0.2s ease;
}

.gallery-nav:hover {
  background: rgba(37, 99, 235, 0.55);
  transform: translateY(-50%) scale(1.08);
}

.gallery-nav.prev {
  left: 14px;
}

.gallery-nav.next {
  right: 14px;
}

.gallery-dots {
  position: absolute;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  display: flex;
  gap: 0.4rem;
}

.gallery-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  padding: 0;
  transition: transform 0.2s ease, background 0.2s ease, width 0.2s ease;
}

.gallery-dot.active {
  background: #ffffff;
  width: 20px;
  border-radius: 999px;
}

@media (max-width: 760px) {
  .pdrrmo-gallery {
    aspect-ratio: 4 / 5;
  }

  .gallery-nav {
    width: 34px;
    height: 34px;
    font-size: 1.2rem;
  }
}
</style>