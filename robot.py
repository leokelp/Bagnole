import numpy as np
from math import cos,sin,atan2,pi,dist,tan,sqrt




class Robot:
    def __init__(self, h, x, y):
        self.first_iter = True
        self.x = x #Meters
        self.y = y #Meters
        self.theta = pi #Rad
        self.phi = 0  #Rad
        self.v = 1 #Meters/s
        self.v_ = 0
        self.L = 2.46 # Meters
        self.omega = 0
        self.omega_s = 0
        self.p0 = 1
        self.M = 1190
        self.energy_spent = 0

        # Derivatives are indicated with an extra "_"

        self.theta_ = 0
        self.phi_ = 0
        # Reference points

        self.x_ref = 0
        self.y_ref = 10
        self.theta_ref = 0
        self.dist_from_ref_point = 2
        self.distance_error_correction = 0
        # Control variables

        self.e = 0
        self.e_int = 0

        self.theta_err = 0
        self.theta_err_der = 0

        self.Kv = 15
        self.Ki = 0.01
        self.Kh = 2
        self.Khd = 1

    def kinematics(self, h):
        self.x = self.x + h * cos(self.theta) * self.v
        self.y = self.y + h * sin(self.theta) * self.v
        if self.first_iter:
            self.theta = self.theta_ref
            self.first_iter = False
        self.theta = self.theta + (h * tan(self.phi) * self.v) / self.L
        self.phi = self.phi + self.phi_ * h
        if abs(self.phi) > pi/8:
            self.phi = sign(self.phi) * pi/8


    # Finds the closest point to the robot and chooses a few points ahead for the reference points
    def find_initial_ref_point(self, ref_point_traj):
        distance_list = np.empty(ref_point_traj.shape[0])
        for i, point in enumerate(ref_point_traj):
            distance_list[i] = dist((self.x, self.y), point)
        closest_point = np.argmin(distance_list)
        self.ref_point_counter = closest_point + self.dist_from_ref_point
        self.ref_point_counter = min(self.ref_point_counter, len(ref_point_traj) -1)
        self.distance_error_correction = dist(ref_point_traj[closest_point],ref_point_traj[self.ref_point_counter])
        self.x_ref = ref_point_traj[self.ref_point_counter][0]
        self.y_ref = ref_point_traj[self.ref_point_counter][1]
        self.theta_ref = atan2((self.y_ref-self.y),(self.x_ref-self.x))

        return



    def control_param(self, h):
        self.e = sqrt((self.x_ref-self.x)**2 + (self.y_ref-self.y)**2) - self.distance_error_correction/2
        self.e_int += self.e

        past_err = self.theta_err
        self.theta_err = angdiff(self.theta_ref, self.theta)
        self.theta_err_der = (self.theta_err - past_err)/h

    def set_new_param(self, ref_traj, h):
        old_v = self.v
        self.v = self.Kv * self.e + self.Ki * self.e_int
        self.phi_ = self.Kh * self.theta_err + self.Khd * self.theta_err_der
        if not self.first_iter:
            self.v_ = (self.v - old_v) / h
        self.energy_spent += (self.M * self.v * self.v_ + self.p0) * h

        #Stop the car at destination
        if dist((self.x,self.y), ref_traj[-1]) < 3:
            self.v = 0


def sign(x):
    if x > 0:
        return 1
    elif x < 0 :
        return -1
    else:
        return 0

def angdiff(x1,x2):
    angle = (x1-x2) % (2*pi)
    while angle > pi:
        angle -= 2*pi
    return angle
