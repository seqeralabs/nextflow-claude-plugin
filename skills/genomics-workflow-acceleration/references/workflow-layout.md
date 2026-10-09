<!-- Adapted for the Nextflow plugin: generic host tools and OAuth MCP. -->
# Optional Acceleration Organization

Edit the user's existing workflow and respect its organization. Add optional
GPU behavior alongside CPU behavior, selected by an explicit runtime toggle
that defaults off. Do not prescribe a new directory tree or copied workflow.

## Toggle

Nextflow may use `params.use_parabricks` or `params.accelerated`, defaulting
to `false`. Python may use `--use-parabricks` or `USE_PARABRICKS`, defaulting
off. Choose names consistent with the user's existing interface.

Document the selected runtime, toggle usage, consolidation opportunities, and
validated changes in an acceleration record chosen by the user. Preserve any
existing documentation rather than creating a fixed output file or folder.

## Integration

- Initially keep optional GPU steps parallel to the original CPU steps.
- Consolidate steps only on the GPU branch when the user approves and equivalent
  outputs are demonstrated.
- Keep CPU behavior as the default unless the user explicitly approves a change
  after comparison.
- Connect downstream consumers to whichever branch ran.
- Preserve compatible output names and formats when possible.
- Use user-selected distinct destinations or tags for comparison outputs to
  avoid overwriting either result.

Use a feature branch when appropriate. Do not force-push or rewrite production
history without explicit authorization. Make a separate copy only if the user
requests one, using the location they choose.
