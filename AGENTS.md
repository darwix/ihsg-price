# Repository Guidelines

## Project Structure & Module Organization

Keep application code in the repository's existing source directories and preserve the current layout when adding files. Place automated checks alongside the existing test structure, and keep static assets in the established asset or public directory. If adding a new top-level directory, use a descriptive name and document its purpose in the relevant project documentation.

## Build, Test, and Development Commands

Use commands defined by the repository's package or build configuration. Before submitting changes, run the relevant build, test, and lint commands for the files you changed. For example, use `npm test` only if the project defines that script. Do not introduce a new toolchain or command without a project need.

## Coding Style & Naming Conventions

Follow the formatting and naming patterns already present in nearby files. Preserve the language and framework conventions used by each module. Use clear names that describe a file's or symbol's purpose; keep filenames consistent with their directory. Run the configured formatter or linter when available, and keep changes focused.

## Testing Guidelines

Use the testing framework and test directory already established by the project. Name tests so they identify the behavior or module under test, and add or update focused tests when changing behavior. Run the narrow relevant test command first, then the broader suite when practical. Do not claim tests passed unless you ran them.

## Commit & Pull Request Guidelines

Write concise commit subjects that describe the change. Follow any established convention in recent project history when available. Pull requests should explain the motivation, summarize user-visible changes, list validation commands and results, and link related issues. Include screenshots for visual changes and note configuration or migration steps when needed.

## Security & Configuration

Do not commit credentials, tokens, or local environment files. Use the project's documented configuration mechanism and provide safe examples for any new settings. Validate external input at system boundaries and avoid logging secrets.
