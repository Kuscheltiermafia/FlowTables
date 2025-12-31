# FlowTables Style Guide

This document outlines the color schema, typography, and other visual styles used in the FlowTables project, as extracted from `index.html`.

## 1. Color Palette

The color system is based on CSS variables defined in the `:root` selector, allowing for easy theming and consistency.

| Variable Name | Value | Preview | Description |
| :--- | :--- | :--- | :--- |
| `--color-primary` | `#1f9feb` | <div style="width:50px;height:20px;background-color:#1f9feb;border:1px solid #ccc;"></div> | The main brand color, used for accents, links, and highlights. |
| `--color-secondary` | `#00c0b3` | <div style="width:50px;height:20px;background-color:#00c0b3;border:1px solid #ccc;"></div> | A secondary brand color, used for status indicators and highlights. |
| `--color-accent` | `#8ce298` | <div style="width:50px;height:20px;background-color:#8ce298;border:1px solid #ccc;"></div> | An accent color for special highlights or tertiary elements. |
| `--color-background-light`| `#F8FAFC` | <div style="width:50px;height:20px;background-color:#F8FAFC;border:1px solid #ccc;"></div> | The primary background color for the body and pages. |
| `--color-text-dark` | `#1F3A63` | <div style="width:50px;height:20px;background-color:#1F3A63;border:1px solid #ccc;"></div> | The primary color for body text and headings. |
| `--color-surface` | `white` | <div style="width:50px;height:20px;background-color:white;border:1px solid #ccc;"></div> | Used for surfaces that sit on top of the background, like cards or modals. |
| `--color-border` | `#E2E8F0` | <div style="width:50px;height:20px;background-color:#E2E8F0;border:1px solid #ccc;"></div> | The default color for borders and dividers. |

## 2. Typography

- **Font Family**: The primary font stack is `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`. This is a system-native font stack that ensures high performance and a familiar look across different operating systems.
- **Base Text Color**: `#1F3A63` (var(`--color-text-dark`))
- **Headings (`h1`)**:
    - Font Size: `clamp(2.5rem, 8vw, 4.5rem)` (responsive sizing)
    - Font Weight: `800`
    - Letter Spacing: `-2px`
- **Paragraphs (`p`)**:
    - Font Size: `1.15rem`
    - Color: `#64748b`

## 3. UI Components

### Button (`.btn-main`)

- **Background**: `#1F3A63` (var(`--color-text-dark`))
- **Text Color**: `white`
- **Padding**: `14px 32px`
- **Border Radius**: `12px`
- **Font Weight**: `600`
- **Hover State**:
    - Background: `#1f9feb` (var(`--color-primary`))
    - Transform: `scale(1.08) translateY(-12px)`
    - Box Shadow: `0 25px 30px rgba(0, 0, 0, 0.3)`

### Card (`.card`)

- **Background**: `transparent` (default), `white` (hover)
- **Border**: `1px solid transparent` (default), `1px solid #E2E8F0` (hover)
- **Border Radius**: `20px`
- **Padding**: `40px`
- **Hover State**:
    - Background: `white`
    - Border Color: `var(--color-border)`
    - Box Shadow: `0 20px 40px rgba(0,0,0,0.04)`
    - Transform: `translateY(-5px)`

## 4. Animation

- **Easing Function**: A consistent easing function is used for most transitions to create a smooth and energetic feel.
- **Variable**: `--easing`
- **Value**: `cubic-bezier(0.2, 0.8, 0.2, 1)`
