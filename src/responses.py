'''
Contains models representing generic API responses
'''
from pydantic import BaseModel

class Error(BaseModel):
    '''
    Model for returning when error occured
    '''
    error: str


class Success(BaseModel):
    '''
    Model for returning when operation completed successfully
    without return value
    '''
    success: bool
