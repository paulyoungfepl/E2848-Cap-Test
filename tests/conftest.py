import pytest
import copy
import numpy as np
import pandas as pd
from captest import capdata as pvc
from captest import util
from captest import columngroups as cg

@pytest.fixture
def meas():
    """Create an instance of CapData with example data loaded."""
    meas = pvc.CapData('meas')
    meas.data = pd.read_csv(
        './tests/data/example_measured_data.csv',
        index_col=0,
        parse_dates=True,
        )
    meas.data_filtered = meas.data.copy(deep=True)
    meas.column_groups = cg.ColumnGroups(util.read_json(
        './tests/data/example_measured_data_column_groups.json'
    ))
    meas.trans_keys = copy.deepcopy(meas.column_groups.keys())
    meas.set_regression_cols(
        power='meter_power', poa='irr_poa_pyran', t_amb='temp_amb', w_vel='wind'
    )
    return meas

@pytest.fixture
def location_and_system():
    """Create a dictionary with a nested dictionary for location and system."""
    loc_sys = {
        'location': {
            'latitude': 30.274583,
            'longitude': -97.740352,
            'altitude': 500,
            'tz': 'America/Chicago',
        },
        'system': {
            'surface_tilt': 20,
            'surface_azimuth': 180,
            'albedo': 0.2,
        }
    }
    return loc_sys

@pytest.fixture
def nrel():
    nrel = pvc.CapData('nrel')
    nrel.data = pd.read_csv(
        './tests/data/nrel_data.csv', index_col=0, parse_dates=True
    )
    nrel.data_filtered = nrel.data.copy()
    nrel.column_groups = {
        'irr-ghi-': ['Global CMP22 (vent/cor) [W/m^2]', ],
        'irr-poa-': ['POA 40-South CMP11 [W/m^2]', ],
        'temp--': ['Deck Dry Bulb Temp [deg C]', ],
        'wind--': ['Avg Wind Speed @ 19ft [m/s]', ],
    }
    nrel.trans_keys = list(nrel.column_groups.keys())
    nrel.regression_cols = {
        'power': '', 'poa': 'irr-poa-', 't_amb': 'temp--', 'w_vel': 'wind--'
    }
    return nrel

@pytest.fixture
def pvsyst():
    # load pvsyst csv file
    df = pd.read_csv(
        './tests/data/pvsyst_example_HourlyRes_2.CSV',
        skiprows=9,
        encoding='latin1',
    ).iloc[1:, :]
    df['Timestamp'] = pd.to_datetime(df['date'])
    df = df.set_index('Timestamp', drop=True)
    df = df.drop(columns=['date']).astype(np.float64)
    df.rename(columns={'T Amb': 'T_Amb'}, inplace=True)
    # set pvsyst DataFrame to CapData data attribute
    pvsyst = pvc.CapData('pvsyst')
    pvsyst.data = df
    pvsyst.data_filtered = pvsyst.data.copy()
    pvsyst.column_groups = {
        'irr-poa-': ['GlobInc'],
        'shade--': ['FShdBm'],
        'index--': ['index'],
        'wind--': ['WindVel'],
        '-inv-': ['EOutInv'],
        'pvsyt_losses--': ['IL Pmax', 'IL Pmin', 'IL Vmax', 'IL Vmin'],
        'temp-amb-': ['T_Amb'],
        'irr-ghi-': ['GlobHor'],
        'temp-mod-': ['TArray'],
        'real_pwr--': ['E_Grid'],
    }
    pvsyst.regression_cols = {
        'power': 'real_pwr--', 'poa': 'irr-poa-', 't_amb': 'temp-amb-', 'w_vel': 'wind--'
    }
    pvsyst.trans_keys = list(pvsyst.column_groups.keys())
    return pvsyst

@pytest.fixture
def pvsyst_irr_filter(pvsyst):
    pvsyst.filter_irr(200, 800)
    pvsyst.tolerance = '+/- 5'
    return pvsyst

@pytest.fixture
def nrel_clear_sky(nrel):
    """ Modeled clear sky data was created using the pvlib fixed tilt clear sky
    models with the following parameters:
         loc = {
            'latitude': 39.742,
            'longitude': -105.18,
            'altitude': 1828.8,
            'tz': 'Etc/GMT+7'
        }
        sys = {'surface_tilt': 40, 'surface_azimuth': 180, 'albedo': 0.2}
    """
    clear_sky = pd.read_csv(
        './tests/data/nrel_data_modelled_csky.csv', index_col=0, parse_dates=True
    )
    nrel.data = pd.concat([nrel.data, clear_sky], axis=1)
    nrel.data_filtered = nrel.data.copy()
    nrel.column_groups['irr-poa-clear_sky'] = ['poa_mod_csky']
    nrel.column_groups['irr-ghi-clear_sky'] = ['ghi_mod_csky']
    nrel.trans_keys = list(nrel.column_groups.keys())
    return nrel