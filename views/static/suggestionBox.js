// suggestionBox.js

function initializeSuggestionBox(inputSelector, selectSelector, suggestions) {
    $(document).on("click", inputSelector, function () {
        var selectContainer = $(this)
            .closest(".autocomplete-select")
            .find(selectSelector);

        createSelectOptions(selectContainer, suggestions);
        selectContainer.toggle();
    });

    $(document).on("keyup", inputSelector, function () {
        var input = $(this).val();
        var suggestionsFiltered = filterSuggestions(input, suggestions);

        var selectContainer = $(this)
            .closest(".autocomplete-select")
            .find(selectSelector);
        createSelectOptions(selectContainer, suggestionsFiltered);
    });

    $(document).on("click", selectSelector + " option", function () {
        var selectedValue = $(this).val();
        var inputField = $(this)
            .closest(".autocomplete-select")
            .find(inputSelector);
        inputField.val(selectedValue);
        $(this).closest(".autocomplete-select").find(selectSelector).hide();
    });
}

function createSelectOptions(container, suggestions) {
    container.html("");
    suggestions.forEach(function (suggestion) {
        container.append(
            '<option value="' + suggestion + '">' + suggestion + "</option>"
        );
    });
}

function filterSuggestions(input, suggestions) {
    if (input.trim() !== "") {
        return suggestions.filter(function (item) {
            return item.toLowerCase().indexOf(input.toLowerCase()) > -1;
        });
    }
    return suggestions;
}
