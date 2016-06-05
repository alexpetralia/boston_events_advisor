    $(document).ready(function () {
        $(":radio").on("click", function () { 
               var value = $(this).val();
               $(this).closest('label').toggleClass('btn-primary');
               $(this).val(value == 1 ? 0 : 1);
        });
    });
    $('#pin').pincodeInput({
        inputs: 4,
        hideDigits: true,
    });
    $('#pincode-input1').pincodeInput();