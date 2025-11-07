# Design Guidelines: Grade 1 Learning Platform

## Design Approach
**Reference-Based Approach** - Drawing inspiration from Khan Academy Kids, Duolingo, and PBS Kids educational platforms, optimized for 6-7 year old children.

**Core Principle**: Create a joyful, safe, and intuitive learning environment that encourages exploration without overwhelming young learners.

---

## Color Palette

**Primary Colors (Bright & Cheerful)**
- Primary Blue: 210 85% 55% (sky blue - calming yet energetic)
- Success Green: 145 70% 50% (bright green - positive reinforcement)
- Warning Orange: 25 95% 60% (warm orange - attention without alarm)
- Error Red: 355 85% 60% (soft red - gentle correction)

**Background Colors**
- Light Mode Base: 45 40% 96% (warm cream - easy on eyes)
- Card Background: 0 0% 100% (pure white)
- Teacher Dashboard: 220 20% 96% (cool professional gray)

**Accent Colors**
- Math Purple: 270 70% 65% (fun, distinct from English)
- English Teal: 175 60% 55% (calm, language-friendly)
- Star Gold: 45 95% 55% (rewards and achievements)

---

## Typography

**Font Families**
- Primary: 'Fredoka', sans-serif (rounded, friendly, highly legible for children)
- Secondary: 'Inter', sans-serif (teacher interface, system text)

**Font Scales**
- Display (Hero): text-5xl to text-7xl, font-bold (large welcome messages)
- Heading: text-3xl to text-4xl, font-semibold (section titles)
- Body: text-2xl, font-medium (content for children - LARGE for readability)
- Teacher UI: text-base to text-lg, font-normal (compact professional text)
- Button Text: text-xl, font-semibold (easy to read action labels)

---

## Layout System

**Spacing Primitives**: Use Tailwind units of 3, 4, 6, 8, 12, 16
- Tight spacing: p-3, m-4 (compact teacher dashboard)
- Standard spacing: p-6, gap-8 (student interface cards)
- Generous spacing: py-12, px-16 (section padding for breathing room)

**Grid System**
- Student Interface: Single column on mobile, max 2 columns on tablet/desktop (simple, focused)
- Teacher Dashboard: Multi-column grid (3-4 columns for lecture/quiz management)
- Max Content Width: max-w-6xl for student areas, max-w-7xl for teacher dashboards

---

## Component Library

### Student Interface Components

**Quiz Cards**
- Large rounded cards (rounded-3xl) with soft shadows
- Each question in its own card with generous padding (p-8)
- Large radio buttons or touch-friendly answer buttons (min-h-16)
- Bright border on selection (border-4 border-primary)
- Immediate visual feedback with color change

**Progress Indicators**
- Large progress bar at top (h-6 rounded-full)
- Animated fill with gradient background
- Star icons showing completed questions
- Clear "X of 10 questions" text in text-2xl

**Lecture Summary Display**
- Illustrated cards with large text (text-2xl line-height-relaxed)
- Bullet points with emoji icons for visual interest
- "Continue" button always visible at bottom (sticky)
- Soft pastel background colors alternating by section

**Score & Review Screen**
- Large celebratory header with star animation
- Score displayed as huge number (text-8xl) with percentage
- Each question review in expandable accordion
- Green checkmarks and red X marks (extra large icons)
- Encouragement messages ("Great job!" "Try again!")

### Teacher Interface Components

**Lecture Upload Area**
- Drag-and-drop zone with dashed border
- PDF icon and upload button
- Summary input: Large textarea (min-h-48) with character counter
- "Generate Summary" button (if using AI assist)

**Quiz Builder**
- Clean form with 10 question slots
- Each question: Input field + 4 answer options + correct answer selector
- Visual numbering (large circled numbers)
- Save draft / Publish toggle
- Preview mode showing student view

**Dashboard Cards**
- Student progress cards with avatars
- Quiz completion statistics
- Recently uploaded lectures grid
- Clean white cards with subtle shadows

### Navigation

**Student Navigation**
- Bottom tab bar (mobile) with large icons and labels
- Tabs: "Learn" (book icon), "Quiz" (pencil icon), "Stars" (star icon)
- Active state with bold color and slight scale
- Fixed position for easy thumb access

**Teacher Navigation**
- Top horizontal nav bar
- Links: Dashboard, Lectures, Quizzes, Students, Settings
- Dropdown profile menu
- Professional, compact design

---

## Animations

**Use Sparingly - Child-Focused Only**
- Star burst on quiz completion (brief, celebratory)
- Gentle bounce on correct answer selection
- Smooth slide transitions between quiz questions
- Progress bar fill animation
- NO distracting background animations
- NO auto-playing content

---

## Images

**Hero Image**: Yes - Large illustration of happy children learning
- Placement: Top of student dashboard/home screen
- Style: Colorful, diverse children with books and devices
- Treatment: Bright, flat illustration style (not realistic photos)
- Dimensions: Full width, 40vh height on desktop

**Subject Icons**
- Math: Calculator or numbers illustration
- English: ABC blocks or book illustration
- Large, colorful SVG icons (w-24 h-24 minimum)

**Achievement Badges**
- Star collections for completed quizzes
- Trophy illustrations for milestones
- Placed on student profile and completion screens

---

## Accessibility for Young Learners

**Touch Targets**: Minimum 56px (h-14) for all interactive elements
**Contrast**: WCAG AAA for all text (young eyes need clarity)
**Reading Level**: Use simple words, short sentences
**Visual Hierarchy**: Color + size + spacing (not just color alone)
**Error States**: Gentle, encouraging language ("Oops! Try again!")
**Loading States**: Fun animations (bouncing dots, spinning stars)

---

## Role-Specific Experiences

**Student View**
- Bright, playful colors throughout
- Large touch-friendly buttons
- Minimal text, maximum visuals
- Clear "what to do next" guidance
- Celebration moments for achievements

**Teacher View**
- Professional, clean interface
- Data tables and analytics
- Efficient forms and bulk actions
- Muted color palette (blues and grays)
- Dense information layouts acceptable