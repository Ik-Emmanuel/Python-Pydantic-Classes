
import json
import pydantic 
from typing import Optional, List


#### custom error definition
class ISBN10FormatError(Exception):
    """Custom error that is raised when ISBN10 doesn't have the right format."""
    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)

class ISBNMissingError(Exception):
    """Custom error that is raised when both ISBN10 and ISBN13 are missing."""

    def __init__(self, title: str, message: str) -> None:
        self.title = title
        self.message = message
        super().__init__(message)



class Book(pydantic.BaseModel):
    """Represents a book with that you can read from a JSON file."""

    title: str
    author: str
    publisher: str
    price: float
    isbn_10: Optional[str]
    isbn_13: Optional[str]
    subtitle: Optional[str]
    
    #creating a validator to check entire model
    #pre=True specifies that it checks before it converts into a model not after 
    @pydantic.root_validator(pre=True) 
    @classmethod
    def check_isbn_10_or_13(cls, values):
        """Make sure there is either an isbn_10 or isbn_13 value defined"""

        if "isbn_10" not in values and "isbn_13" not in values:
            raise ISBNMissingError(
                title=values["title"],
                message="Document should have either an ISBN10 or ISBN13",
            )
        return values


    #element wise validaton (on a particular field)
    @pydantic.validator("isbn_10")
    @classmethod
    def isbn_10_valid(cls, value):
        """ Validator that checks that the isbn number is valid """
        chars = [c for c in value if c in "0123456789Xx"]
        if len(chars) != 10:
            raise ISBN10FormatError(value=value, message="ISBN10 should be 10 digits")
        #else

        def char_to_int(char: str) -> int:
            if char in "Xx":
                return 10
            return int(char)
        
        #checking to see if weighted sum is divisible by 11 -ISBN validation 
        weighted_sum  =sum((10-i) * char_to_int(x) for i, x in enumerate(chars))
        if weighted_sum %11 != 0:
            raise ISBN10FormatError(
                value=value, message="ISBN10 should be divisible by 11"
            )
    
    class Config:
        """Pydantic config class"""
        allow_mutation = False   #prevent data alterations 
        # anystr_lower = True 
     


def main() -> None:
    """ main function"""

    with open ("./data.json") as file:
        data = json.load(file)
        books: List[Book] = [Book(**item) for item in data]
        print(books[1].title)
        #pydantic allows you to easily access the values as attributes 
        # books[1].title = "your new title" #this wont work if class config allow_mutation = False
        print(books[1].dict(exclude={"price"})) #return all but this one
        print(books[1].dict(include={"price", "publisher"})) #only return these



if __name__ == "__main__":
    main()