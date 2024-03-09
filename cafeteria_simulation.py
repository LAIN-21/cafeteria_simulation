import simpy
import random
import numpy as np
import csv
from statistics import mean
import pandas as pd

#-------------------------- Student Generator -----------------------------------------------------------------------------------------------------------------------
class Cafeteria:
    def __init__(self, env, menu_waitress_capacity, poke_waitress_capacity, self_decision_waitress_capacity, container_capacity):
        self.env = env
        self.menu_service_waitress = simpy.Resource(env, capacity=menu_waitress_capacity)
        self.poke_service_waitress = simpy.Resource(env, capacity=poke_waitress_capacity)
        self.self_decision_waitress = simpy.Resource(env, capacity=self_decision_waitress_capacity)
        self.container = simpy.Container(env, init=container_capacity, capacity=container_capacity)

        self.no_food_count = 0
        self.self_decision_count = 0
        self.poke_count = 0
        self.menu_count = 0
        self.warm_up = 500

        self.total_menu_queue_time = []
        self.total_poke_queue_time = []
        self.total_self_decision_queue_time = []

    def student_arrival_time(self, interarrival_time1, interarrival_time2):
        while True:
            yield self.env.timeout(random.expovariate(1/interarrival_time1))
            yield self.env.timeout(random.expovariate(1/interarrival_time2))
            student = self.student_behaviour()
            self.env.process(student)

    def student_behaviour(self):
        service_types = ['no_food', 'self_decision', 'poke', 'menu']
        weights = [5, 15, 30, 50]

        service_type = random.choices(service_types, weights=weights)[0]

        if service_type == 'no_food':
            if self.env.now > self.warm_up:
                self.no_food_count += 1
            yield self.env.timeout(0)
        elif service_type == 'self_decision':
            if self.env.now > self.warm_up:
                self.self_decision_count += 1
            yield self.env.process(self.self_decision_service())
        elif service_type == 'poke':
            if self.env.now > self.warm_up:
                self.poke_count += 1
            yield self.env.process(self.poke_service())
        elif service_type == 'menu':
            if self.env.now > self.warm_up:
                self.menu_count += 1
            yield self.env.process(self.menu_service())

    def menu_service(self):
        start_time = self.env.now
        with self.menu_service_waitress.request() as request:
            yield request
            queue_time = self.env.now - start_time
            if self.env.now > self.warm_up:
                self.total_menu_queue_time.append(queue_time)
            yield self.env.timeout(4)
            yield self.env.timeout(2)

    def poke_service(self):
        start_time = self.env.now
        with self.poke_service_waitress.request() as request:
            yield request
            queue_time = self.env.now - start_time
            if self.env.now > self.warm_up:
                self.total_poke_queue_time.append(queue_time)
            yield self.env.timeout(6)
            yield self.env.timeout(2)

    def self_decision_service(self):
        start_time = self.env.now
        with self.self_decision_waitress.request() as request:
            yield request
            queue_time = self.env.now - start_time
            if self.env.now > self.warm_up:
                self.total_self_decision_queue_time.append(queue_time)
            yield self.env.timeout(4)

def main():
    n_runs = 100
    random.seed(2024)
    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Run', 'Mean Menu Queue Time', 'Mean Poke Queue Time', 'Mean Self Decision Queue Time', 'Mean Total Queue', 'Menu Count', 'Poke Count', 'Self-Decision Count', 'No Food Count', 'Total Order Count', 'Menu Revenue (€)', 'Poke Revenue (€)', 'Self Decision Revenue (€)', 'Total Revenue (€)'])
    
    for run in range (n_runs):
        env = simpy.Environment()
        cafeteria = Cafeteria(env, menu_waitress_capacity=4, poke_waitress_capacity=2, self_decision_waitress_capacity=2, container_capacity=50)

        sim_duration = 3600
        total_duration = cafeteria.warm_up + sim_duration
        env.process(cafeteria.student_arrival_time(interarrival_time1=4, interarrival_time2=3))
        env.run(until=total_duration)

        mean_menu_queue_time = mean(cafeteria.total_menu_queue_time)
        mean_poke_queue_time = mean(cafeteria.total_poke_queue_time)
        mean_self_decision_queue_time = mean(cafeteria.total_self_decision_queue_time)
        mean_queue = mean([mean_menu_queue_time, mean_poke_queue_time, mean_self_decision_queue_time])

        menu_count = cafeteria.menu_count
        poke_count = cafeteria.poke_count
        self_decision_count = cafeteria.self_decision_count
        no_food_count = cafeteria.no_food_count
        total_order_count = menu_count + poke_count + self_decision_count

        menu_revenue = menu_count*8.9
        poke_revenue = poke_count*11
        self_decision_revenue = self_decision_count*4
        total_revenue = menu_revenue + poke_revenue + self_decision_revenue

        list_results = [run, mean_menu_queue_time, mean_poke_queue_time, mean_self_decision_queue_time, mean_queue, menu_count, poke_count, self_decision_count, no_food_count, total_order_count, menu_revenue, poke_revenue, self_decision_revenue, total_revenue]
        with open('results.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(list_results)

    df = pd.read_csv('results.csv')
    average_mean_menu_queue_time = df['Mean Menu Queue Time'].mean()
    average_mean_poke_queue_time = df['Mean Poke Queue Time'].mean()
    average_mean_self_decision_queue_time = df['Mean Self Decision Queue Time'].mean()
    average_mean_queue = df['Mean Total Queue'].mean()

    average_menu_count = df['Menu Count'].mean()
    average_poke_count = df['Poke Count'].mean()
    average_self_decision_count = df['Self-Decision Count'].mean()
    average_no_food_count = df['No Food Count'].mean()
    average_total_order_count = df['Total Order Count'].mean()

    average_menu_revenue = df['Menu Revenue (€)'].mean()
    average_poke_revenue = df['Poke Revenue (€)'].mean()
    average_self_decision_revenue = df['Self Decision Revenue (€)'].mean()
    average_total_revenue = df['Total Revenue (€)'].mean()

    print(f"Average Menu Queing Time: {average_mean_menu_queue_time}")
    print(f"Average Poke Queing Time: {average_mean_poke_queue_time}")
    print(f"Average Self Decision Queing Time: {average_mean_self_decision_queue_time}")
    print(f"Average Queue: {average_mean_queue}")

    print(f"Average Menu Count: {average_menu_count}")
    print(f"Average Poke Count: {average_poke_count}")
    print(f"Average Self Decision Count: {average_self_decision_count}")
    print(f"Average No Food Count: {average_no_food_count}")
    print(f"Average Total Orders: {average_total_order_count}")

    print(f"Average Revenue from Menus: {average_menu_revenue}")
    print(f"Average Revenue from Pokes: {average_poke_revenue}")
    print(f"Average Revenues from Self Decisions: {average_self_decision_revenue}")
    print(f"Average Total Revenue: {average_total_revenue}")

if __name__ == "__main__":
    main()