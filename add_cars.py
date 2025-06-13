from app import create_app, db
from app.models import Car, TransmissionType, FuelType

def add_cars():
    app = create_app()
    with app.app_context():
        car1 = Car(
            model_id=1,
            year=2020,
            doors=4,
            seats=5,
            fuel=FuelType.petrol,
            transmission=TransmissionType.manual,
            power=150,
            price_per_day=40.0,
            description="Prvi auto opis"
        )
        car2 = Car(
            model_id=1,
            year=2021,
            doors=2,
            seats=2,
            fuel=FuelType.diesel,
            transmission=TransmissionType.automatic,
            power=200,
            price_per_day=60.0,
            description="Drugi auto opis"
        )
        db.session.add(car1)
        db.session.add(car2)
        db.session.commit()
        print("Dodana su dva auta!")

if __name__ == "__main__":
    add_cars()
