$(function () {

      /*
      Set the text and the color of the answer's dropdown button, with the
      values of the checked answer.
      */
      function setAnswerDropButton() {
          let $this = $(this),
              $button = $this.parents(".dropdown-menu").siblings('.dropdown-toggle'),
              $cell = $this.parents('td')
          $button.text($this.data("text"))
          $cell.removeClass("bg-"+$button.data("previous-answer"))
          $cell.addClass("bg-"+$this.val())
          $button.data("previous-answer", $this.val())
          $button.dropdown('hide')
      }

      /*
      On page's load, set the answers' dropdown buttons if an answer is already
      checked.
      This is set by a script, because firefox keep cached the precedent form change
      after a page reload.
       */
      $('input[type="radio"][name="answer"]:checked').each(setAnswerDropButton)

      // Set the answer's dropdown button on every answer change
      $('input[type="radio"][name="answer"]').on("change", setAnswerDropButton)

      /*
      Reset all the answers' forms and their dropdown buttons on reset button click
       */
      $('#reset_answers').on('click', function () {
          $('.answer_form').each(function (i,e) {
              let $form = $(e),
                  $button = $form.siblings('.dropdown-toggle'),
                  $cell = $form.parents('td')
                  $initialInput = $form.find("input[checked]"),
                  initial_text = "",
                  initial_value = "NONE"
              if ($initialInput.length) {
                  initial_text = $initialInput.data("text")
                  initial_value = $initialInput.val()
              }
              $form.trigger("reset")
              $cell.removeClass("bg-"+$button.data("previous-answer"))
              $button.text(initial_text)
              $cell.addClass("bg-"+initial_value)
              $button.data("previous-answer", initial_value)

          })

      })

      /*
      On submit button click, gather all the changed answers and put them in
      the 'data' array as a json string {answer: answer, event: event.pk}.
      Post the data to the submit url, and reload the page on success
       */
      $('#submit_answers').on('click', function () {
          let data = $('input[name="csrfmiddlewaretoken"]').serializeArray()
          $('.answer_form').each(function (i, e) {
              let $form = $(e),
                  answer = $form.find('input[name="answer"]:checked').val()
              if (answer && answer !== $form.data('initial-answer')) {
                  data.push({
                      name: 'participation',
                      value: JSON.stringify({
                          answer: answer,
                          event: $form.find('input[name="event"]').val()
                      })
                  })
              }
          })
          $.post($(this).data('post-url'), data).done(function (msg) {
              alert(msg)
              // Reload the page to display the modifications on the table
              location.reload()
          }).fail(function (jqXHR) {
              alert("Http code "+jqXHR.status+" "+jqXHR.responseText)
          })
      })

  })