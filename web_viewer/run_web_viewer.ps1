Param(
    [string]$PythonPath = ".\.venv\Scripts\python.exe"
)

if (!(Test-Path $PythonPath)) {
    Write-Host "Python do venv nao encontrado em $PythonPath"
    Write-Host "Crie o ambiente virtual e tente novamente."
    exit 1
}

& $PythonPath -m pip install -r "web_viewer/requirements.txt"
& $PythonPath -m streamlit run "web_viewer/app_streamlit.py"
