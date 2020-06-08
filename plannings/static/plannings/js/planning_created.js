$(function () {

      /*
      Copy the planning's link in the clipboard when the copy button is clicked
      -create a hidden temp input
      -set the link as the input value
      -force the focus on the input
      -use the command 'copy'
      -delete the temp input
       */
      $("#copy_button").on("click", function () {
          let $temp = $("<input/>")
          $("body").append($temp)
          $temp.val($('#planning_link').attr("href")).select()
          let success = document.execCommand("copy")
          $temp.remove()
          if (success) {
              alert("Lien copié")
          } else {
              alert("Erreur, le lien n'a pas pu être copié")
          }
      })

  })