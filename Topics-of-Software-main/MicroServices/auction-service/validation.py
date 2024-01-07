# validation functions for submit listing, photo with listing, and place bid
from datetime import date

def validate_new_listing(form_data):
    """
    validates form data from submit_listing for required fields:
         expiration
    param form_data -- information stored in request.form (dict)
    return error -- str or None
    """
    error = None
    today = date.today()
    try:
        form_date = form_data['expiration'].split('-')
        expiration_date = date(month=int(form_date[1]), day=int(form_date[2]), year=int(form_date[0]))
    except:
        expiration_date = None

    if not form_data['expiration'] or expiration_date is None or expiration_date <= today:
        error = "Please add an expiration date that is at least 1 day from today to this listing."
        print(error)
        return error
    else:
        return error


def validate_photo(file_request):
    """
    function determines whether request contains a file or not
    param file_request -- contains request information of user photo (dict)
    return -- True if image present, False otherwise (bool)
    """
    return True if file_request.filename != '' else False

def validate_bid(user_bid, high_bid):
    """
    determines whether bid amount from user higher than current high bid.
    param user_bid -- user submitted bid information from db (int)
    param high_bid -- current high bid associated with listing (dict)
    return (validity, message) -- tuple of (False, str)
    """
    message = f"Congratulations! Your bid of ${user_bid} placed successfully."
    if high_bid is None:
        message = "Darn. wtf is going on..."
        return False, message
    if user_bid < high_bid["startPrice"]:
        message = "Your bid should be higher than the start price! Try again."
        return False, message
    if high_bid["amount"] is not None and user_bid <= high_bid["amount"]:
        message = "Your bid is not high enough! Try again."
        return False, message
    return True, message