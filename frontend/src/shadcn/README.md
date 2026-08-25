# shadcn boundary

This directory contains code managed by or required by shadcn:

- `components/ui/`: generated UI component source
- `hooks/`: hooks used by shadcn components
- `lib/`: shadcn component utilities
- `styles.css`: Tailwind entry, theme tokens, and shadcn global styles

Application components and feature styles should stay outside this directory.
When adding a component with the shadcn CLI, keep `components.json` aliases pointed here.
