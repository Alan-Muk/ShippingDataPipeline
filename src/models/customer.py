from pydantic import BaseModel


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class Street(BaseModel):
    number: int
    name: str


class Location(BaseModel):
    street: Street
    city: str
    state: str
    country: str
    postcode: str | int
    coordinates: Coordinates


class Name(BaseModel):
    title: str
    first: str
    last: str


class Login(BaseModel):
    uuid: str


class Registered(BaseModel):
    date: str


class Customer(BaseModel):
    login: Login
    name: Name
    gender: str
    email: str
    phone: str
    location: Location
    registered: Registered
    nat: str
