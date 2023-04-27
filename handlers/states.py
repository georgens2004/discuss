from aiogram.fsm.state import State, StatesGroup

class HomeState(StatesGroup):
    main = State()

class MyTopicsState(StatesGroup):
    main = State()
    topic = State()
    creating = State()

class SurfingTopicsState(StatesGroup):
    choosing = State()
    chose = State()
