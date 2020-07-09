import numpy as np
import math
import time
import threading
import utils

'''
Originally from https://github.com/abhijitmajumdar/Quadcopter_simulator
'''

def Feedback_Linearization(t, v, state, m, Ix, Iy, Iz):
    '''Credit to https://www.kth.se/polopoly_fs/1.588039.1550155544!/Thesis%20KTH%20-%20Francesco%20Sabatino.pdf'''
    p, q, r = state[11:14]
    cs, ct, cp = np.cos(state[3:6])
    ss, st, sp = np.sin(state[3:6])
    ts, tt, tp = np.tan(state[3:6])

    zeta = state[9]
    xi = state[10]
    # d_i,j = L_gj * L_f^(r_i-1) (h_i(x))
    delta = np.array([[-(sp * ss + st * cp * cs)/m,
                       zeta * (sp * st * cs - ss * cp) / (Ix * m),
                       -(zeta * cs * ct) / (Iy * m),
                       0],
                      [(-sp * cs + ss * st * cp) / m,
                       -zeta * (sp * ss * st + cp * cs) / (Ix * m),
                       zeta * ss * ct / (Iy * m),
                       0],
                      [-cp * ct / m,
                       zeta * sp * ct / (Ix * m),
                       zeta * st / (Iy * m),
                       0],
                      [0,
                       0,
                       sp/(Iy*ct),
                       cp/(Iz*ct)]])

    b = np.array([xi*(-(q*cp - r*sp)*cp*cs*ct/m - (sp*cs - ss*st*cp)*(q*sp/ct + r*cp/ct)/m - (-sp*st*cs + ss*cp)*(p + q*sp*tt + r*cp*tt)/m) + (q*cp - r*sp)*(-xi*cp*cs*ct/m + zeta*(q*cp - r*sp)*st*cp*cs/m - zeta*(sp*cs - ss*st*cp)*(q*sp*st/ct**2 + r*st*cp/ct**2)/m - zeta*(q*(tt**2 + 1)*sp + r*(tt**2 + 1)*cp)*(-sp*st*cs + ss*cp)/m + zeta*(q*sp/ct + r*cp/ct)*ss*cp*ct/m + zeta*(p + q*sp*tt + r*cp*tt)*sp*cs*ct/m) + (q*sp/ct + r*cp/ct)*(-xi*(sp*cs - ss*st*cp)/m + zeta*(q*cp - r*sp)*ss*cp*ct/m - zeta*(-sp*ss - st*cp*cs)*(q*sp/ct + r*cp/ct)/m - zeta*(sp*ss*st + cp*cs)*(p + q*sp*tt + r*cp*tt)/m) + (p + q*sp*tt + r*cp*tt)*(-xi*(-sp*st*cs + ss*cp)/m - zeta*(-q*sp - r*cp)*cp*cs*ct/m + zeta*(q*cp - r*sp)*sp*cs*ct/m - zeta*(-sp*ss - st*cp*cs)*(p + q*sp*tt + r*cp*tt)/m - zeta*(sp*cs - ss*st*cp)*(q*cp/ct - r*sp/ct)/m - zeta*(q*sp/ct + r*cp/ct)*(sp*ss*st + cp*cs)/m - zeta*(q*cp*tt - r*sp*tt)*(-sp*st*cs + ss*cp)/m) + p*r*(-Ix + Iz)*(-zeta*(sp*cs - ss*st*cp)*sp/(m*ct) - zeta*(-sp*st*cs + ss*cp)*sp*tt/m - zeta*cp**2*cs*ct/m)/Iy - q*r*zeta*(Iy - Iz)*(-sp*st*cs + ss*cp)/(Ix*m),
                  xi*((q*cp - r*sp)*ss*cp*ct/m - (-sp*ss - st*cp*cs)*(q*sp/ct + r*cp/ct)/m - (sp*ss*st + cp*cs)*(p + q*sp*tt + r*cp*tt)/m) + (q*cp - r*sp)*(xi*ss*cp*ct/m - zeta*(q*cp - r*sp)*ss*st*cp/m - zeta*(-sp*ss - st*cp*cs)*(q*sp*st/ct**2 + r*st*cp/ct**2)/m - zeta*(q*(tt**2 + 1)*sp + r*(tt**2 + 1)*cp)*(sp*ss*st + cp*cs)/m + zeta*(q*sp/ct + r*cp/ct)*cp*cs*ct/m - zeta*(p + q*sp*tt + r*cp*tt)*sp*ss*ct/m) + (q*sp/ct + r*cp/ct)*(-xi*(-sp*ss - st*cp*cs)/m + zeta*(q*cp - r*sp)*cp*cs*ct/m - zeta*(-sp*cs + ss*st*cp)*(q*sp/ct + r*cp/ct)/m - zeta*(sp*st*cs - ss*cp)*(p + q*sp*tt + r*cp*tt)/m) + (p + q*sp*tt + r*cp*tt)*(-xi*(sp*ss*st + cp*cs)/m + zeta*(-q*sp - r*cp)*ss*cp*ct/m - zeta*(q*cp - r*sp)*sp*ss*ct/m - zeta*(-sp*ss - st*cp*cs)*(q*cp/ct - r*sp/ct)/m - zeta*(-sp*cs + ss*st*cp)*(p + q*sp*tt + r*cp*tt)/m - zeta*(q*sp/ct + r*cp/ct)*(sp*st*cs - ss*cp)/m - zeta*(q*cp*tt - r*sp*tt)*(sp*ss*st + cp*cs)/m) + p*r*(-Ix + Iz)*(-zeta*(-sp*ss - st*cp*cs)*sp/(m*ct) - zeta*(sp*ss*st + cp*cs)*sp*tt/m + zeta*ss*cp**2*ct/m)/Iy - q*r*zeta*(Iy - Iz)*(sp*ss*st + cp*cs)/(Ix*m),
                  xi*((q*cp - r*sp)*st*cp/m + (p + q*sp*tt + r*cp*tt)*sp*ct/m) + (q*cp - r*sp)*(xi*st*cp/m + zeta*(q*cp - r*sp)*cp*ct/m + zeta*(q*(tt**2 + 1)*sp + r*(tt**2 + 1)*cp)*sp*ct/m - zeta*(p + q*sp*tt + r*cp*tt)*sp*st/m) + (p + q*sp*tt + r*cp*tt)*(xi*sp*ct/m + zeta*(-q*sp - r*cp)*st*cp/m - zeta*(q*cp - r*sp)*sp*st/m + zeta*(q*cp*tt - r*sp*tt)*sp*ct/m + zeta*(p + q*sp*tt + r*cp*tt)*cp*ct/m) + p*r*(-Ix + Iz)*(zeta*sp**2*ct*tt/m + zeta*st*cp**2/m)/Iy + q*r*zeta*(Iy - Iz)*sp*ct/(Ix*m),
                  (q*cp - r*sp)*(q*sp*st/ct**2 + r*st*cp/ct**2) + (q*cp/ct - r*sp/ct)*(p + q*sp*tt + r*cp*tt) + p*r*(-Ix + Iz)*sp/(Iy*ct)])
    # u = alpha + beta * v
    try:
        d_inv = np.linalg.inv(delta)
        alpha = -d_inv @ b
        beta = d_inv
        u_bar = alpha + beta @ v
        return u_bar
    except np.linalg.LinAlgError:
        print("Matrix Non-Invertible!")
        return [0,0,0,0]

class Controller_PID_Point2Point:
    def __init__(self, get_state, get_time, actuate_motors, params, quad_identifier):
        self.quad_identifier = quad_identifier
        self.actuate_motors = actuate_motors
        self.get_state = get_state
        self.get_time = get_time
        self.MOTOR_LIMITS = params['Motor_limits']
        self.TILT_LIMITS = [(params['Tilt_limits'][0] / 180.0) * np.pi, (params['Tilt_limits'][1] / 180.0) * np.pi]
        self.YAW_CONTROL_LIMITS = params['Yaw_Control_Limits']
        self.Z_LIMITS = [self.MOTOR_LIMITS[0] + params['Z_XY_offset'], self.MOTOR_LIMITS[1] - params['Z_XY_offset']]
        self.LINEAR_P, self.LINEAR_I, self.LINEAR_D = params['Linear_PID'].values()
        self.ANGULAR_P, self.ANGULAR_I, self.ANGULAR_D = params['Angular_PID'].values()
        self.LINEAR_TO_ANGULAR_SCALER = params['Linear_To_Angular_Scaler']
        self.YAW_RATE_SCALER = params['Yaw_Rate_Scaler']
        self.xi_term = 0
        self.yi_term = 0
        self.zi_term = 0
        self.thetai_term = 0
        self.phii_term = 0
        self.gammai_term = 0
        self.xi_term_sim = 0
        self.yi_term_sim = 0
        self.zi_term_sim = 0
        self.thetai_term_sim = 0
        self.phii_term_sim = 0
        self.gammai_term_sim = 0
        self.thread_object = None
        self.target = [0, 0, 0]
        self.yaw_target = 0.0
        self.run = True

    def update(self, state=None, sim=False):
        if sim:
            xi, yi, zi = self.xi_term_sim, self.yi_term_sim, self.zi_term_sim
            thetai, phii, gammai = self.thetai_term_sim, self.phii_term_sim, self.gammai_term_sim
            x, y, z, x_dot, y_dot, z_dot, theta, phi, gamma, theta_dot, phi_dot, gamma_dot = state
        else:
            xi, yi, zi = self.xi_term, self.yi_term, self.zi_term
            thetai, phii, gammai = self.thetai_term, self.phii_term, self.gammai_term
            x, y, z, x_dot, y_dot, z_dot, theta, phi, gamma, theta_dot, phi_dot, gamma_dot = self.get_state(
                self.quad_identifier)
        dest_x, dest_y, dest_z = self.target
        x_error = dest_x - x
        y_error = dest_y - y
        z_error = dest_z - z
        xi += self.LINEAR_I[0] * x_error
        yi += self.LINEAR_I[1] * y_error
        zi += self.LINEAR_I[2] * z_error
        dest_x_dot = self.LINEAR_P[0] * x_error - self.LINEAR_D[0] * x_dot + xi
        dest_y_dot = self.LINEAR_P[1] * y_error - self.LINEAR_D[1] * y_dot + yi
        dest_z_dot = self.LINEAR_P[2] * z_error - self.LINEAR_D[2] * z_dot + zi
        throttle = np.clip(dest_z_dot, self.Z_LIMITS[0], self.Z_LIMITS[1])
        dest_theta = self.LINEAR_TO_ANGULAR_SCALER[0] * (dest_x_dot * math.sin(gamma) - dest_y_dot * math.cos(gamma))
        dest_phi = self.LINEAR_TO_ANGULAR_SCALER[1] * (dest_x_dot * math.cos(gamma) + dest_y_dot * math.sin(gamma))
        dest_gamma = self.yaw_target
        dest_theta, dest_phi = np.clip(dest_theta, self.TILT_LIMITS[0], self.TILT_LIMITS[1]), np.clip(dest_phi,
                                                                                                      self.TILT_LIMITS[
                                                                                                          0],
                                                                                                      self.TILT_LIMITS[
                                                                                                          1])
        theta_error = dest_theta - theta
        phi_error = dest_phi - phi
        gamma_dot_error = (self.YAW_RATE_SCALER * utils.wrap_angle(dest_gamma - gamma)) - gamma_dot
        thetai += self.ANGULAR_I[0] * theta_error
        phii += self.ANGULAR_I[1] * phi_error
        gammai += self.ANGULAR_I[2] * gamma_dot_error
        x_val = self.ANGULAR_P[0] * theta_error + self.ANGULAR_D[0] * (-theta_dot) + thetai
        y_val = self.ANGULAR_P[1] * phi_error + self.ANGULAR_D[1] * (-phi_dot) + phii
        z_val = self.ANGULAR_P[2] * gamma_dot_error + gammai
        z_val = np.clip(z_val, self.YAW_CONTROL_LIMITS[0], self.YAW_CONTROL_LIMITS[1])
        m1 = throttle + x_val + z_val
        m2 = throttle + y_val - z_val
        m3 = throttle - x_val + z_val
        m4 = throttle - y_val - z_val
        M = np.clip([m1, m2, m3, m4], self.MOTOR_LIMITS[0], self.MOTOR_LIMITS[1])
        if not sim:
            self.actuate_motors(self.quad_identifier, M)
        return M

    def update_target(self, target):
        self.target = target

    def update_yaw_target(self, target):
        self.yaw_target = utils.wrap_angle(target)

    def thread_run(self, update_rate, time_scaling):
        update_rate = update_rate * time_scaling
        last_update = self.get_time()
        while self.run:
            time.sleep(0)
            self.time = self.get_time()
            if (self.time - last_update).total_seconds() > update_rate:
                self.update()
                last_update = self.time

    def start_thread(self, update_rate=0.005, time_scaling=1):
        self.thread_object = threading.Thread(target=self.thread_run, args=(update_rate, time_scaling))
        self.thread_object.start()

    def stop_thread(self):
        self.run = False

    def reset_sim(self):
        self.xi_term_sim = self.xi_term
        self.yi_term_sim = self.yi_term
        self.zi_term_sim = self.zi_term
        self.thetai_term_sim = self.thetai_term
        self.phii_term_sim = self.phii_term
        self.gammai_term_sim = self.gammai_term


class Controller_PID_Velocity(Controller_PID_Point2Point):
    def update(self):
        [dest_x, dest_y, dest_z] = self.target
        [x, y, z, x_dot, y_dot, z_dot, theta, phi, gamma, theta_dot, phi_dot, gamma_dot] = self.get_state(
            self.quad_identifier)
        x_error = dest_x - x_dot
        y_error = dest_y - y_dot
        z_error = dest_z - z
        self.xi_term += self.LINEAR_I[0] * x_error
        self.yi_term += self.LINEAR_I[1] * y_error
        self.zi_term += self.LINEAR_I[2] * z_error
        dest_x_dot = self.LINEAR_P[0] * (x_error) + self.LINEAR_D[0] * (-x_dot) + self.xi_term
        dest_y_dot = self.LINEAR_P[1] * (y_error) + self.LINEAR_D[1] * (-y_dot) + self.yi_term
        dest_z_dot = self.LINEAR_P[2] * (z_error) + self.LINEAR_D[2] * (-z_dot) + self.zi_term
        throttle = np.clip(dest_z_dot, self.Z_LIMITS[0], self.Z_LIMITS[1])
        dest_theta = self.LINEAR_TO_ANGULAR_SCALER[0] * (dest_x_dot * math.sin(gamma) - dest_y_dot * math.cos(gamma))
        dest_phi = self.LINEAR_TO_ANGULAR_SCALER[1] * (dest_x_dot * math.cos(gamma) + dest_y_dot * math.sin(gamma))
        dest_gamma = self.yaw_target
        dest_theta, dest_phi = np.clip(dest_theta, self.TILT_LIMITS[0], self.TILT_LIMITS[1]), np.clip(dest_phi,
                                                                                                      self.TILT_LIMITS[
                                                                                                          0],
                                                                                                      self.TILT_LIMITS[
                                                                                                          1])
        theta_error = dest_theta - theta
        phi_error = dest_phi - phi
        gamma_dot_error = (self.YAW_RATE_SCALER * utils.wrap_angle(dest_gamma - gamma)) - gamma_dot
        self.thetai_term += self.ANGULAR_I[0] * theta_error
        self.phii_term += self.ANGULAR_I[1] * phi_error
        self.gammai_term += self.ANGULAR_I[2] * gamma_dot_error
        x_val = self.ANGULAR_P[0] * (theta_error) + self.ANGULAR_D[0] * (-theta_dot) + self.thetai_term
        y_val = self.ANGULAR_P[1] * (phi_error) + self.ANGULAR_D[1] * (-phi_dot) + self.phii_term
        z_val = self.ANGULAR_P[2] * (gamma_dot_error) + self.gammai_term
        z_val = np.clip(z_val, self.YAW_CONTROL_LIMITS[0], self.YAW_CONTROL_LIMITS[1])
        m1 = throttle + x_val + z_val
        m2 = throttle + y_val - z_val
        m3 = throttle - x_val + z_val
        m4 = throttle - y_val - z_val
        M = np.clip([m1, m2, m3, m4], self.MOTOR_LIMITS[0], self.MOTOR_LIMITS[1])
        self.actuate_motors(self.quad_identifier, M)
