# sardinia_map.py
#
# Còdixi partziu po scarrigai sa mapa de sa Sardìnnia po dda
# amostai in infogràficas.
#
# Copyright 2022 Sustainable Sardinia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import geopandas as gp
import wget
import zipfile
import tempfile
import os


def _download_and_unzip(url, file_name):
    system_temp_dir = tempfile.gettempdir()
    zipped_filename = os.path.join(system_temp_dir, file_name + ".zip")
    if not os.path.exists(zipped_filename):
        zipped_filename = wget.download(url, out=system_temp_dir)

    temporary_dir = tempfile.TemporaryDirectory().name
    with zipfile.ZipFile(zipped_filename, "r") as zip_ref:
        zip_ref.extractall(temporary_dir)
    return temporary_dir


def _download_comune_limits():
    """The limits of the comune are provided by Regione Sardegna with license
    CC BY 4.0.

    Source: http://dati.regione.sardegna.it/dataset/limiti-amministrativi-comunali
    """
    file_name = "limitiAmministrComunali"
    dir_with_files = _download_and_unzip(
        "http://webgis.regione.sardegna.it/scaricocartografiaETL/limitiAmministrativi/limitiAmministrComunali/limitiAmministrComunali.zip",
        file_name,
    )
    shapefile = os.path.join(dir_with_files, file_name + ".shp")

    map_data = gp.read_file(shapefile)
    map_data = map_data.loc[:, ["nome", "codIstatCo", "geometry"]]
    return map_data


def _download_toponyms():
    """The toponyms are provided by Regione Sardegna with license
    CC BY 4.0.

    Source: http://dati.regione.sardegna.it/dataset/toponimi-capoluoghi-comunali-della-sardegna/resource/8ad16549-874f-40fc-aa44-0f08822907a6
    """
    file_name = "TOP_macroToponimi"
    dir_with_files = _download_and_unzip(
        "http://webgis.regione.sardegna.it/scaricocartografiaETL/toponimi/macrotoponimi/TOP_macroToponimi.zip",
        file_name,
    )
    shapefile = os.path.join(dir_with_files, file_name + ".shp")

    toponyms_data = gp.read_file(shapefile)
    toponyms_data = toponyms_data.loc[:, ["topoItalia", "topoSardo", "codIstCom"]]

    # Fix issues with toponyms
    toponyms_data.loc[
        toponyms_data["topoItalia"] == "Ollastra Simaxis", "codIstCom"
    ] = "095037"
    toponyms_data["topoSardo"] = toponyms_data["topoSardo"].apply(
        lambda n: n.replace("XIU", "XU")
    )

    return toponyms_data


def _normalize_accents(text):
    import unicodedata

    try:
        text = unicode(text, "utf-8")
    except NameError:
        pass
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return text


def _remove_apostrophes(text):
    return text.replace("'", "")


def standardise_toponym(toponym):
    """Given a string, standardise the toponym by removing
    accents and special characters."""
    return _remove_apostrophes(_normalize_accents(toponym)).upper()


def get_sardinia_map():
    """Get the map of Sardinia."""
    comune_limits = _download_comune_limits()
    toponyms = _download_toponyms()

    map_data = comune_limits.merge(
        toponyms, how="inner", left_on="codIstatCo", right_on="codIstCom"
    )
    map_data = map_data.loc[:, ["codIstatCo", "geometry", "nome", "topoSardo"]]
    map_data["code"] = map_data["nome"].apply(standardise_toponym)

    map_data.rename(
        columns={"nome": "topoIta", "topoSardo": "topoSrd", "codIstatCo": "istatCode"},
        inplace=True,
    )

    return map_data
