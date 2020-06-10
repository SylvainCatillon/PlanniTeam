$(function () {

    // Change the eye icon on intro toggle
    $("#intro_text").on("hide.bs.collapse", function () {
        $("#intro_collapse_button").html('<i class="far fa-eye"></i>')
    }).on("show.bs.collapse", function () {
        $("#intro_collapse_button").html('<i class="far fa-eye-slash"></i>')
    })

    // Set the boundary as viewport for all the dropdowns
    $(".dropdown-toggle").dropdown({boundary: 'viewport'})


    // Avoid dropdown close on click inside
    $(".dropdown-menu").on("click", function (event) {
        event.stopPropagation()

    })

    function formatDate(iso_date) {
        let date = new Date(iso_date),
            options = {day: '2-digit', month: 'short', year: 'numeric'}
        return date.toLocaleDateString('fr-FR', options)
    }


    /*
    Add the event's information to the planning's form, in a hidden container
    Thus, when the planning's form is submitted, it also contains
    the events' information
     */
    function addEventToForm($event_form) {
        let $container = $('<div></div>', {'hidden': 'hidden'})
        $event_form.find('input, textarea').each(function () {
            let hidden_id = 'hidden-'+this.id,
                $input = $('#'+hidden_id)
            if ($input.length) {
                if (this.type === "checkbox") {
                    $input.prop('checked', this.checked)
                } else {
                    $input.val(this.value)
                }
            } else {
                $input = $(this).clone()
                $input.attr('id', hidden_id)
            }
            $container.append($input)

        })
        $("#planning_form").append($container)
    }

    function setEventCard($card) {
        let $form = $card.find('.event_form')
        addEventToForm($form)
        $card.find(".card-header, .card-text").each(function (i, elem) {
            let $elem = $(elem),
                field = $elem.data("field"),
                val = $form.find('[name$="' + field + '"]').val()
            if (field === 'date') {
                val = formatDate(val)
            }
            $elem.text(val)

        })
        if ($form.find('[name$="DELETE"]').prop("checked")) {
            $card.addClass("event_card--deleted")
        } else {
            $card.removeClass("event_card--deleted")
        }
    }

    // Set the data of the existing events
    $("#created_events_container .event_card").each(function () {
        setEventCard($(this))
    })

    // Show the 'edit guests' container if the 'protected' input
    // is already checked on page load
    if ($('#id_protected').prop("checked")) {
        $("#edit_guests_container").show()
    }

    // Show the options to choose guests only if input 'protected' is checked
    $("#id_protected").on("change", function () {
        let $guests_container = $("#edit_guests_container")
        if (this.checked) {
            $guests_container.show()
        } else {
            $guests_container.hide()
        }
    });

    /*
    When the 'add guest form' is submitted:
    -check that the guest's email isn't already added
    -add the email in the guests display
    -add an option with the email as value to the guest's email select
    -add a hidden input with the guest's email as value
    -reset the input
     */
    $("#add_guest_form").on("submit", function (event) {
        event.preventDefault()
        let $input = $('input[name="add_guest"]'),
            email = $input.val(),
            $guests_select = $("#guest_emails_select"),
            $guests_container = $('#guests_display')

        if ($guests_select.text().includes(email)) {
            alert("Vous avez déjà indiqué cette adresse")
        } else {
            $guests_container.append($("<p></p>", {
                id: "id_" + email,
                text: email
            }))
            $guests_select.append($("<option></option>", {
                value: email,
                text: email
            }))
            $('#planning_form').append($("<input>", {
                value: email,
                type: "hidden",
                name: 'guest_email'
            }))
            $guests_container.scrollTop(
                $guests_container[0].scrollHeight)
            $input.val("")
        }
    });


    /*
    For each selected guest email option:
    -Remove the select option
    -Remove the associate hidden input
    -Remove the email from the guests display
     */
    $("#delete_guest_submit").on("click", function (event) {
        event.preventDefault()
        let data = $('#guest_emails_select').serializeArray()
        $.each(data, function (i, field) {
            $('option[value="' + field.value + '"]').remove()
            $('input[name="guest_email"][value="' + field.value + '"]').remove()
            $('p[id="id_' + field.value + '"]').remove()
        })
    });

    /*
    Function launched after a successful server validation
    on an existing event modification
     */
    function validExistingEvent($card) {
        setEventCard($card)
        $card.find('.dropdown-toggle').dropdown('hide')
        let $created_events_container = $('#created_events_container')
        $card.parent().appendTo($created_events_container)
        $created_events_container.scrollTop(
            $created_events_container[0].scrollHeight)

        $("#success_alert").fadeTo(2000, 500).slideUp(500, function () {
            $("#success_alert").slideUp(500);
        });

    }

    /*
    Function launched after a successful server validation
    on an new event
     */
    function validNewEvent($form, data) {
        let $formContainer = $form.parent(),
            $new_event = $('#model_event_card').find('.event_card_container').clone(),
            $card = $new_event.find('.card'),
            formset_prefix = $form.data('prefix').replace(/__prefix__/g, ""),
            $total_forms_input = $('input[name="' + formset_prefix + 'TOTAL_FORMS"]'),
            form_number = $total_forms_input.val(),
            $created_events_container = $("#created_events_container")

        $card.append($formContainer.html().replace(/__prefix__/g, form_number))

        // Set the new event dropdown button
        let $dropdownButton = $card.find('.dropdown-toggle')
        $dropdownButton.text('Modifier')
        $dropdownButton.dropdown({boundary: 'viewport'})

        // Set the data of the new event form and card
        $.each(data, function () {
            let $input = $card.find('[name$="' + this.name + '"]')
            if ($input.length && $input.attr('type') !== "hidden") {
                $input.val(this.value)
            }

        })
        setEventCard($card)
        // Show the delete input and label
        $card.find('[name$="DELETE"]').parent().show()

        //Set the onClick function of validate event button
        $card.find('.validate_event').on('click', function (event) {
            event.preventDefault()
            validateEvent($(this).parents(".event_form"))

        })

        //Reset the 'add event' form
        $formContainer.find('input, textarea').each(function () {
            let $this = $(this),
                type = $this.attr('type')
            if ($this.val() && type !== "hidden") {
                if (type === 'checkbox') {
                    $this.prop('checked', false)
                } else {
                    $this.val("")
                }
            }

        })

        // Increase the value of the TOTAL_FORMS input
        $total_forms_input.val(parseInt(form_number) + 1)

        $created_events_container.append($new_event)
        $created_events_container.scrollTop(
            $created_events_container[0].scrollHeight)
        $('.dropdown-toggle').dropdown('hide')

    }

    function validateEvent($eventForm) {
        let data = $('input[name="csrfmiddlewaretoken"]').serializeArray(),
            prefix = $eventForm.data("prefix") + "-";

        // Remove the previous errors of the form
        $eventForm.find(".field_errors li").each(function (i, error) {
            error.remove()
        });

        // Gather the form's data, and remove the formset prefix, because
        // the 'check event' function use the original form, not the formset
        $eventForm.find('input, textarea').each(function () {
            if ($(this).val()) {
                let value = $(this).serializeArray()[0]
                if (value) {
                    value.name = value.name.replace(prefix, "")
                    data.push(value)
                }
            }
        })

        // Post the data to the 'check event' function
        $.post($eventForm.attr('action'), data).done(function () {
            if (prefix.includes('__prefix__')) {
                validNewEvent($eventForm, data)
            } else {
                validExistingEvent($eventForm.parents('.card'))
            }

        }).fail(function (jqXHR) {
            if (jqXHR.status === 422) {
                let data = JSON.parse(jqXHR.responseText)
                $.each(data, function (field) {
                    let $errorsContainer = $("#id_" + prefix + field + "_errors"),
                        $input = $("#id_" + prefix + field)
                    $input.val(function () {
                        return this.defaultValue

                    })
                    $.each(data[field], function (i, error) {
                        $errorsContainer.append($('<li>' + error.message + '</li>'))

                    })
                })
            } else {
                alert("Une erreur s'est produite, veuillez réessayer. Erreur HTTP " + jqXHR.status)
            }

        });
    }

    $('.event_form').on('submit', function (event) {
        event.preventDefault()
        validateEvent($(this))

    })

})