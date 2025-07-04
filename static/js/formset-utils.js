export function reindexFormset(formsetSelector, totalFormsSelector) {
    console.log("Reindexing formset");
    console.log(formsetSelector)
    const formset = document.querySelector(`${formsetSelector}`);
    const rows = formset.querySelectorAll(`.formset-form:not(.hidden)`);
    const totalFormsInput = document.querySelector(totalFormsSelector);

    // Determine the prefix based on the formset selector
    let prefix = 'recipe_ingredient';
    if (formsetSelector === '#image-formset') {
        prefix = 'recipe_image';
    }
    if (formsetSelector === '#preparation-step-formset') {
        prefix = 'recipe_preparation_step';
    }

    rows.forEach((row, index) => {
        // Update row ID
        const newRowId = `${prefix}-${index}`;
        row.id = newRowId;

        console.log(row)
        // Update order input inside this row
        const orderInput = row.querySelector(`[id$='-ORDER']`);
        if (orderInput) {
            orderInput.value = index;
        }

        // Update label only inside this row (if applicable)
        const stepLabel = row.querySelector('.step-label');
        if (stepLabel) {
            stepLabel.textContent = `${index + 1}.`;
        }

        // Update all relevant attributes within this row
        row.querySelectorAll('[name], [id], label[for]').forEach((el) => {
            ['name', 'id', 'for'].forEach((attr) => {
                if (el.hasAttribute(attr)) {
                    el.setAttribute(attr,
                        el.getAttribute(attr).replace(
                            new RegExp(`${prefix}-\\d+|form-\\d+`, 'g'),
                            `${prefix}-${index}`
                        )
                    );
                }
            });
        });
    });

    if (totalFormsInput) {
        totalFormsInput.value = rows.length;
    }
}
