// MinaFox SearXNG category guard.
// SearXNG's Simple theme uses checkboxes so users can select multiple
// categories. MinaFox intentionally behaves like a calmer tab bar: selecting
// one category clears the others, and at least one category remains selected.
(() => {
  const categoryInputs = () => Array.from(
    document.querySelectorAll('#categories input[type="checkbox"][name^="category_"]')
  );

  const keepSingleCategory = (selected) => {
    const inputs = categoryInputs();
    if (!inputs.length) return;

    if (selected && selected.checked) {
      inputs.forEach((input) => {
        if (input !== selected) input.checked = false;
      });
      return;
    }

    // At least one MinaFox category stays selected so searches remain valid.
    if (!inputs.some((input) => input.checked)) {
      (selected || inputs[0]).checked = true;
    }
  };

  const init = () => {
    const inputs = categoryInputs();
    if (!inputs.length) return;

    const checked = inputs.filter((input) => input.checked);
    if (checked.length > 1) keepSingleCategory(checked[0]);
    if (checked.length === 0) inputs[0].checked = true;

    inputs.forEach((input) => {
      input.addEventListener('change', () => keepSingleCategory(input));
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
