# -*- coding: utf-8 -*-
"""
HardClamDrift v3 — Individual-Based Model for Hard Clam (Meretrix meretrix)
Two-stage development with stage-specific temperature parameters

This advanced version includes:
- Stage-specific optimal temperature ranges
- Sublethal temperature exposure tracking
- Enhanced temperature effect assessment

Key Features:
- Two-stage accumulated temperature development: egg (benthic) → larva (pelagic)
- Event recording: hatching/settlement time, location, and distance
- Temperature exposure statistics: optimal, sublethal, and lethal ranges
- Optional diel vertical migration (DVM)

Compatible with: OpenDrift 1.14.x
"""

from __future__ import annotations
import numpy as np
from typing import Optional
from opendrift.models.oceandrift import Lagrangian3DArray, OceanDrift


def haversine_km(lon1, lat1, lon2, lat2):
    """Calculate great-circle distance in km."""
    R = 6371.0
    lon1r, lat1r = np.radians(lon1), np.radians(lat1)
    lon2r, lat2r = np.radians(lon2), np.radians(lat2)
    dlon = lon2r - lon1r
    dlat = lat2r - lat1r
    a = np.sin(dlat/2.0)**2 + np.cos(lat1r)*np.cos(lat2r)*np.sin(dlon/2.0)**2
    c = 2.0*np.arcsin(np.sqrt(a))
    return R * c


class HardClamElement(Lagrangian3DArray):
    """Particle element with biological and thermal tracking variables."""

    variables = Lagrangian3DArray.add_variables([
        # Release information
        ('release_id',     {'dtype': np.int32,   'default': -1}),
        ('release_day',    {'dtype': np.int32,   'default': -1}),  # YYYYMMDD
        ('release_lon',    {'dtype': np.float32, 'default': np.nan}),
        ('release_lat',    {'dtype': np.float32, 'default': np.nan}),

        # Development stage
        ('stage',          {'dtype': np.int8,    'default': 0}),   # 0=egg, 1=larva
        ('age_h',          {'dtype': np.float32, 'default': 0.0}),
        ('acc_deg_h',      {'dtype': np.float32, 'default': 0.0}), # Accumulated degree-hours
        ('progress',       {'dtype': np.float32, 'default': 0.0}), # Development progress (0-1)
        ('competent',      {'dtype': np.int8,    'default': 0}),   # Ready to settle
        ('competent_time_h', {'dtype': np.float32, 'default': np.nan}),

        # Hatching event
        ('hatch_time_h',      {'dtype': np.float32, 'default': np.nan}),
        ('hatch_lon',         {'dtype': np.float32, 'default': np.nan}),
        ('hatch_lat',         {'dtype': np.float32, 'default': np.nan}),
        ('hatch_distance_km', {'dtype': np.float32, 'default': np.nan}),

        # Settlement event
        ('settled_flag',      {'dtype': np.int8,    'default': 0}),
        ('settle_time_h',     {'dtype': np.float32, 'default': np.nan}),
        ('settle_lon',        {'dtype': np.float32, 'default': np.nan}),
        ('settle_lat',        {'dtype': np.float32, 'default': np.nan}),
        ('settle_distance_km',{'dtype': np.float32, 'default': np.nan}),

        # Final distance (updated continuously)
        ('final_distance_km', {'dtype': np.float32, 'default': np.nan}),

        # High temperature exposure (lethal)
        ('hot_hours',    {'dtype': np.float32, 'default': 0.0}),
        ('hot_run',      {'dtype': np.float32, 'default': 0.0}),
        ('hot_run_max',  {'dtype': np.float32, 'default': 0.0}),

        # Low temperature exposure
        ('cold_hours',   {'dtype': np.float32, 'default': 0.0}),
        ('cold_run',     {'dtype': np.float32, 'default': 0.0}),
        ('cold_run_max', {'dtype': np.float32, 'default': 0.0}),

        # Optimal temperature exposure (stage-specific)
        ('opt_hours_egg',   {'dtype': np.float32, 'default': 0.0}),
        ('opt_hours_larva', {'dtype': np.float32, 'default': 0.0}),

        # Sub-optimal temperature exposure
        ('opt_below_hours_egg',   {'dtype': np.float32, 'default': 0.0}),
        ('opt_above_hours_egg',   {'dtype': np.float32, 'default': 0.0}),
        ('opt_below_hours_larva', {'dtype': np.float32, 'default': 0.0}),
        ('opt_above_hours_larva', {'dtype': np.float32, 'default': 0.0}),

        # Sublethal temperature exposure (v3 specific)
        ('sublethal_hours_total',  {'dtype': np.float32, 'default': 0.0}),
        ('sublethal_hours_egg',    {'dtype': np.float32, 'default': 0.0}),
        ('sublethal_hours_larva',  {'dtype': np.float32, 'default': 0.0}),
        ('sublethal_run_max',      {'dtype': np.float32, 'default': 0.0}),
        ('sublethal_deg_h_total',  {'dtype': np.float32, 'default': 0.0}),

        # Stage duration and temperature integrals
        ('egg_hours',            {'dtype': np.float32, 'default': 0.0}),
        ('larva_hours',          {'dtype': np.float32, 'default': 0.0}),
        ('temp_time_sum_egg',    {'dtype': np.float32, 'default': 0.0}),  # ∫T dt
        ('temp_time_sum_larva',  {'dtype': np.float32, 'default': 0.0}),

        # Near-bottom exposure (larval stage)
        ('near_bottom_hours_larva', {'dtype': np.float32, 'default': 0.0}),

        # Temperature deviation integrals (degree-hours)
        ('cold_deg_h_egg',   {'dtype': np.float32, 'default': 0.0}),
        ('hot_deg_h_egg',    {'dtype': np.float32, 'default': 0.0}),
        ('cold_deg_h_larva', {'dtype': np.float32, 'default': 0.0}),
        ('hot_deg_h_larva',  {'dtype': np.float32, 'default': 0.0}),
    ])


class HardClamDrift(OceanDrift):
    """Main model for Hard clam drift simulation with biological processes."""

    ElementType = HardClamElement

    required_variables = {
        'x_sea_water_velocity':  {'fallback': 0},
        'y_sea_water_velocity':  {'fallback': 0},
        'sea_surface_height':    {'fallback': 0},
        'upward_sea_water_velocity': {'fallback': 0, 'profiles': True},
        'sea_water_temperature': {'fallback': 0, 'profiles': True},
        'sea_floor_depth_below_sea_level': {'fallback': 10000.0},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Physics defaults
        self.set_config('drift:horizontal_diffusivity', 5.0)
        self.set_config('drift:vertical_advection', True)
        self.set_config('drift:vertical_mixing', False)
        self.set_config('drift:stokes_drift', False)

        # Biological parameters
        self.T0_egg: float = 12.9    # Egg development threshold (°C)
        self.K_egg: float = 259.0    # Egg development requirement (degree-hours)
        self.T0_larva: float = 19.0  # Larval development threshold (°C)
        self.K_larva: float = 840.0  # Larval development requirement (degree-hours)

        self.alpha_bottom: float = 0.5  # Bottom flow coefficient

        # Stage-specific optimal temperatures (v3 feature)
        # Based on literature: Kim et al., 2010; 2011
        self.Topt_low_egg: float = 25.0   # Egg optimal range: 25-27°C
        self.Topt_high_egg: float = 27.0
        self.Topt_low_larva: float = 27.0  # Larval optimal range: 27-29°C
        self.Topt_high_larva: float = 29.0

        # Temperature thresholds
        self.T_sublethal: float = 30.0  # Sublethal threshold (development success drops)
        self.Tcrit: float = 33.0        # Lethal threshold (no survival)

        # Mortality settings
        self.hotkill_hours: Optional[float] = None   # Cumulative lethal hours
        self.hotkill_consec: Optional[float] = None  # Consecutive lethal hours
        self.cold_stagnant_days: Optional[float] = 4.0  # Days without development

        # Behavioral parameters
        self.dvm_speed: float = 0.0  # Diel vertical migration speed (m/s)

        # Settlement options
        self.stop_when_larva_complete: bool = True
        self.settle_require_bottom: bool = False
        self.settle_bottom_buffer_m: float = 1.0

        # Internal tracking
        self._t0 = None
        self._sublethal_run = None

    def _hours_since_start(self) -> float:
        """Calculate hours elapsed since simulation start."""
        if self._t0 is None:
            return 0.0
        return (self.time - self._t0).total_seconds() / 3600.0

    def update(self):
        """Main update loop for each timestep."""
        # Initialize on first frame
        if self._t0 is None:
            self._t0 = self.time
            self._sublethal_run = np.zeros(self.elements.lon.size, dtype=np.float32)

        # 1) Horizontal advection
        self.advect_ocean_current()

        # 2) Vertical advection (if enabled)
        if self.get_config('drift:vertical_advection'):
            self.vertical_advection()

        # 3) Vertical mixing (if enabled)
        if self.get_config('drift:vertical_mixing'):
            self.vertical_mixing()

        # 4) Biological processes
        self._biology()

        # 5) Update final distance for all active elements
        e = self.elements
        active = np.ones(e.lon.size, dtype=bool)
        e.final_distance_km[active] = haversine_km(
            e.release_lon[active], e.release_lat[active],
            e.lon[active], e.lat[active]
        )

    def _biology(self):
        """Biological development and temperature response."""
        e = self.elements
        dt_h = self.time_step.total_seconds() / 3600.0

        # Get environmental conditions
        T = self.environment.sea_water_temperature
        depth = self.environment.sea_floor_depth_below_sea_level

        # === Lethal temperature exposure ===
        is_hot_all = (T >= float(self.Tcrit))
        e.hot_hours += is_hot_all.astype(float) * dt_h
        e.hot_run = np.where(is_hot_all, e.hot_run + dt_h, 0.0)
        e.hot_run_max = np.maximum(e.hot_run_max, e.hot_run)

        # Check for heat-induced mortality
        to_kill_hot = np.zeros(e.lon.size, dtype=bool)
        if self.hotkill_hours is not None and self.hotkill_hours > 0:
            to_kill_hot |= (e.hot_hours >= float(self.hotkill_hours))
        if self.hotkill_consec is not None and self.hotkill_consec > 0:
            to_kill_hot |= (e.hot_run >= float(self.hotkill_consec))
        if np.any(to_kill_hot):
            self.deactivate_elements(to_kill_hot, reason='hotkill')

        # === Sublethal temperature exposure (v3 feature) ===
        is_sublethal_all = (T >= float(self.T_sublethal))
        e.sublethal_hours_total += is_sublethal_all.astype(float) * dt_h

        if self._sublethal_run is not None:
            self._sublethal_run = np.where(is_sublethal_all,
                                          self._sublethal_run + dt_h, 0.0)
            e.sublethal_run_max = np.maximum(e.sublethal_run_max, self._sublethal_run)

        # Temperature excess integral
        e.sublethal_deg_h_total += np.maximum(0.0, T - float(self.T_sublethal)).astype(float) * dt_h

        # === Egg stage (stage=0) ===
        egg = (e.stage == 0)
        if np.any(egg):
            # Accumulated temperature development
            dT1 = np.maximum(0.0, T[egg] - float(self.T0_egg))
            e.acc_deg_h[egg] += dT1 * dt_h
            e.progress[egg] = np.minimum(1.0, e.acc_deg_h[egg] / float(self.K_egg))

            # Stage statistics
            e.egg_hours[egg] += dt_h
            e.temp_time_sum_egg[egg] += T[egg].astype(float) * dt_h

            # Optimal temperature exposure (egg: 25-27°C)
            low_egg, high_egg = float(self.Topt_low_egg), float(self.Topt_high_egg)
            T_egg = T[egg]
            is_opt_egg = (T_egg >= low_egg) & (T_egg <= high_egg)
            is_below_egg = (T_egg < low_egg)
            is_above_egg = (T_egg > high_egg)
            e.opt_hours_egg[egg] += is_opt_egg.astype(float) * dt_h
            e.opt_below_hours_egg[egg] += is_below_egg.astype(float) * dt_h
            e.opt_above_hours_egg[egg] += is_above_egg.astype(float) * dt_h

            # Temperature deviation integrals
            e.cold_deg_h_egg[egg] += np.maximum(0.0, low_egg - T_egg).astype(float) * dt_h
            e.hot_deg_h_egg[egg] += np.maximum(0.0, T_egg - high_egg).astype(float) * dt_h

            # Sublethal exposure (egg stage)
            is_sublethal_egg = (T_egg >= float(self.T_sublethal))
            e.sublethal_hours_egg[egg] += is_sublethal_egg.astype(float) * dt_h

            # Hatching trigger
            hatch = egg & (e.progress >= 1.0)
            if np.any(hatch):
                e.stage[hatch] = 1
                e.hatch_time_h[hatch] = self._hours_since_start()
                e.hatch_lon[hatch] = e.lon[hatch]
                e.hatch_lat[hatch] = e.lat[hatch]
                e.hatch_distance_km[hatch] = haversine_km(
                    e.release_lon[hatch], e.release_lat[hatch],
                    e.lon[hatch], e.lat[hatch]
                )
                # Reset for larval stage
                e.acc_deg_h[hatch] = 0.0
                e.progress[hatch] = 0.0

        # === Larval stage (stage=1) ===
        larva = (e.stage == 1)
        if np.any(larva):
            e.age_h[larva] += dt_h

            # Accumulated temperature development
            dT2 = np.maximum(0.0, T[larva] - float(self.T0_larva))
            e.acc_deg_h[larva] += dT2 * dt_h
            e.progress[larva] = np.minimum(1.0, e.acc_deg_h[larva] / float(self.K_larva))

            # Competency check
            comp_new = larva & (e.competent == 0) & (e.progress >= 1.0)
            if np.any(comp_new):
                e.competent[comp_new] = 1
                e.competent_time_h[comp_new] = self._hours_since_start()

            # Cold exposure and stagnation
            is_cold = (T[larva] <= float(self.T0_larva))
            e.cold_hours[larva] += is_cold.astype(float) * dt_h
            new_run = e.cold_run[larva] + is_cold.astype(float) * dt_h
            e.cold_run[larva] = np.where(is_cold, new_run, 0.0)
            e.cold_run_max[larva] = np.maximum(e.cold_run_max[larva], e.cold_run[larva])

            # Check for cold stagnation mortality
            if self.cold_stagnant_days is not None and self.cold_stagnant_days > 0:
                limit_h = float(self.cold_stagnant_days) * 24.0
                stagn = larva & (e.progress < 1.0) & (e.cold_run >= limit_h)
                if np.any(stagn):
                    self.deactivate_elements(stagn, reason='larval_cold_stagnant')

            # Stage statistics
            e.larva_hours[larva] += dt_h
            T_larva = T[larva]
            e.temp_time_sum_larva[larva] += T_larva.astype(float) * dt_h

            # Optimal temperature exposure (larva: 27-29°C)
            low_larva, high_larva = float(self.Topt_low_larva), float(self.Topt_high_larva)
            is_opt_larva = (T_larva >= low_larva) & (T_larva <= high_larva)
            is_below_larva = (T_larva < low_larva)
            is_above_larva = (T_larva > high_larva)
            e.opt_hours_larva[larva] += is_opt_larva.astype(float) * dt_h
            e.opt_below_hours_larva[larva] += is_below_larva.astype(float) * dt_h
            e.opt_above_hours_larva[larva] += is_above_larva.astype(float) * dt_h

            # Temperature deviation integrals
            e.cold_deg_h_larva[larva] += np.maximum(0.0, low_larva - T_larva).astype(float) * dt_h
            e.hot_deg_h_larva[larva] += np.maximum(0.0, T_larva - high_larva).astype(float) * dt_h

            # Sublethal exposure (larval stage)
            is_sublethal_larva = (T_larva >= float(self.T_sublethal))
            e.sublethal_hours_larva[larva] += is_sublethal_larva.astype(float) * dt_h

            # Near-bottom exposure
            dloc = depth[larva]
            near_bottom = (-e.z[larva]) >= (dloc - float(self.settle_bottom_buffer_m))
            e.near_bottom_hours_larva[larva] += near_bottom.astype(float) * dt_h

            # Optional diel vertical migration
            if self.dvm_speed and self.dvm_speed > 0.0:
                direction = -1 if self.time.hour < 12 else 1
                dz = direction * float(self.dvm_speed) * self.time_step.total_seconds()
                e.z[larva] = e.z[larva] + dz
                dloc = depth[larva]
                # Constrain between 0.5m and bottom-0.5m
                e.z[larva] = np.minimum(-0.5, e.z[larva])
                e.z[larva] = np.maximum(-dloc + 0.5, e.z[larva])

            # Settlement upon completion
            if self.stop_when_larva_complete:
                done = larva & (e.progress >= 1.0)

                # Filter by bottom proximity if required
                if np.any(done) and self.settle_require_bottom:
                    dloc = depth[done]
                    near_bottom = (-e.z[done]) >= (dloc - float(self.settle_bottom_buffer_m))
                    idx_done = np.where(done)[0][near_bottom]
                else:
                    idx_done = np.where(done)[0]

                if idx_done.size > 0:
                    ht = self._hours_since_start()
                    e.settle_time_h[idx_done] = ht
                    e.settled_flag[idx_done] = 1
                    e.settle_lon[idx_done] = e.lon[idx_done]
                    e.settle_lat[idx_done] = e.lat[idx_done]
                    e.settle_distance_km[idx_done] = haversine_km(
                        e.release_lon[idx_done], e.release_lat[idx_done],
                        e.lon[idx_done], e.lat[idx_done]
                    )
                    mask = np.zeros(e.lon.size, dtype=bool)
                    mask[idx_done] = True
                    self.deactivate_elements(mask, reason='larval_complete')


def add_kz_constant_reader(model: OceanDrift, kz_value: float):
    """Add constant vertical diffusivity reader."""
    from opendrift.readers import reader_constant
    Kz_reader = reader_constant.Reader({'ocean_vertical_diffusivity': float(kz_value)})
    model.add_reader(Kz_reader)