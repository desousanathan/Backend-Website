from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, DecimalField, RadioField, SubmitField
from wtforms.validators import InputRequired, EqualTo, length, NumberRange
from flask_wtf.file import FileField, FileRequired, FileAllowed


class RegistrationFrom(FlaskForm):
    user_id = StringField("User id: ", validators=[InputRequired()])
    password = PasswordField("Password: ", validators=[InputRequired(), length(min=8)])
    password2 = PasswordField("Conform Password: ", validators=[InputRequired(), EqualTo("password")])
    email_address = StringField("Email Address:", validators=[InputRequired()])
    submit = SubmitField("Register!")

class LoginFrom(FlaskForm):
    user_id = StringField("User id:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    submit = SubmitField("Login!")

class ChangePasswordForm(FlaskForm):
    check_password = PasswordField("Current Password:",
                                   validators=[InputRequired()])
    new_password = PasswordField("New Password",
                                 validators=[InputRequired(), length(min=8)])
    new_password2 = PasswordField("Conform Password:",
                                  validators=[InputRequired(), EqualTo("new_password")])
    submit = SubmitField("Change")

class ChangeEmailForm(FlaskForm):
    change_email = StringField("New Email Address:",
                               validators=[InputRequired()])
    submit = SubmitField("Change Email")

#--------------------------------------------------------------------------------------#
class AddNewItem(FlaskForm):
    name = StringField("Name: ", validators=[InputRequired()])
    desc = StringField("Description: ", validators=[InputRequired()])
    num_available = IntegerField("Number of items in stock: ", validators=[InputRequired()])
    price = DecimalField("Price($):", validators=[InputRequired()])
    #_______________________________#
    file = FileField('Choose an image', validators=[InputRequired(), FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], 'Only jpg, jpeg or png are allowed')])
    #_______________________________#
    submit = SubmitField("Add!")

class UpdateItem(FlaskForm):
    prod_id = IntegerField("Product ID:", validators=[InputRequired()])
    name_check = BooleanField("Name:")
    desc_check = BooleanField("Description:")
    num_available_check = BooleanField("Number in stock:")
    price_check = BooleanField("Price:")
    submit = SubmitField("Choose!")

class Update2(FlaskForm):
    name = StringField("New Name:")
    desc = StringField("New Description:")
    num_available = IntegerField("Number of items in stock:")
    price = DecimalField("Price:")
    submit = SubmitField("Add!")


class DeleteItem(FlaskForm):
    prod_id = IntegerField("What is the Product Id of the item you would like to be Deleted?", validators=[InputRequired()])
    submit = SubmitField("Delete!")


class SaleForm(FlaskForm):
    prod_id = IntegerField("Prod Id:", validators=[InputRequired()])
    sale_percent = IntegerField("What is the sale percentage:", validators=[InputRequired()])
    submit = SubmitField("Implement Sale")

class AddCartForm(FlaskForm):
    num_of_items = IntegerField("Numbers To Add:", validators=[NumberRange(min=1)])
    submit = SubmitField("Add!")

class DeleteCartForm(FlaskForm):
    num_of_items = IntegerField("Items To delete:", validators=[InputRequired()])
    submit = SubmitField("Delete")


class SearchForm(FlaskForm):
    searchValue = StringField("Search:", validators=[InputRequired()])
    submit = SubmitField("Search!")

class SuggestForm(FlaskForm):
    suggestion = StringField("Suggestion:",  validators=[InputRequired()])
    submit = SubmitField()

