# Envents Style Guide

## Overview

This document describes the styling approach used in the Envents project. It serves as both documentation and a reference for developers working on the project.

## CSS Architecture

The project uses Tailwind CSS as the primary styling framework, with custom CSS added using the `@layer` directive for proper organization and specificity.

### File Structure

- **Main CSS Source**: `/theme/static_src/src/master-styles.css` (single source of truth for all styles)
- **Compiled Output**: `/static/css/dist/styles.css` (development and production)

> **Important**: All CSS should be added to the master-styles.css file. We no longer use separate CSS files.

### Build Process

1. During development, run:
   ```bash
   cd theme/static_src
   npm run dev
   ```
   This starts a watch process that automatically rebuilds the CSS as you make changes.

2. For production deployment, run:
   ```bash
   ./deploy_production.sh
   ```
   This builds an optimized version of the CSS for production.

## Design System

### Colors

We use the following color palette:

- **Primary**: #3498db (Blue)
- **Success**: #2ecc71 (Green)
- **Warning**: #f39c12 (Orange)
- **Danger**: #e74c3c (Red)
- **Neutral**: Gray scale from 50-900

### Typography

- **Primary Font**: Arial, sans-serif
- **Heading Sizes**:
  - h1: text-4xl (2.25rem)
  - h2: text-3xl (1.875rem)
  - h3: text-2xl (1.5rem)
  - h4: text-xl (1.25rem)
  - h5: text-lg (1.125rem)
  - h6: text-base (1rem)

### Components

#### Buttons

```html
<button class="btn-primary">Primary Button</button>
<button class="btn-secondary">Secondary Button</button>
<button class="btn-success">Success Button</button>
<button class="btn-danger">Danger Button</button>
```

#### Forms

```html
<input type="text" class="form-control" placeholder="Input field" />
```

#### Cards

```html
<div class="card">
  <div class="card-header">Card Header</div>
  <div class="card-body">Card Content</div>
  <div class="card-footer">Card Footer</div>
</div>
```

#### Alerts

```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-danger">Error message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-info">Information message</div>
```

## Responsive Design

The project uses Tailwind's responsive utilities:

- **sm**: 640px and above
- **md**: 768px and above
- **lg**: 1024px and above
- **xl**: 1280px and above
- **2xl**: 1536px and above

Example:
```html
<div class="w-full md:w-1/2 lg:w-1/3">Responsive width</div>
```

## Custom Utilities

We've added some custom utility classes:

- `.text-shadow`: Adds subtle text shadow
- `.text-shadow-none`: Removes text shadow

## Styling Guidelines

1. **Use Tailwind Classes** for most styling needs
2. **Custom Components** should use the `@layer components` directive
3. **Custom Utilities** should use the `@layer utilities` directive
4. **Responsive Design**: Always ensure components work well on all screen sizes
5. **Consistency**: Use the predefined colors and components for a consistent look

## CSS Troubleshooting

If you encounter issues with CSS not loading correctly:

1. **Check the build process**: Run `./build_css.sh` to rebuild the CSS files
2. **Verify the CSS file exists**: The compiled CSS should be at `/static/css/dist/styles.css`
3. **Content-Type issues**: Our build process adds the proper content-type comment to help servers identify the file
4. **S3 Storage issues**: Use the `configure_s3_bucket.py` script to properly configure S3 for CSS files
5. **Development fallback**: In development mode, we include Tailwind directly as a fallback

### Common Issues

- **Circular dependencies**: Do not use `@apply hidden` in CSS components; use `display: none;` instead
- **Missing styles**: Make sure all your custom CSS is added to `master-styles.css`
- **Cache issues**: Add a version parameter to your CSS URL to force a refresh of cached CSS
