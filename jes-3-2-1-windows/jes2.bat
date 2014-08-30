set classpath=".\jars\jython.jar;.\jars\jmf.jar;.\jars\jl1.0.jar;.\jars\junit.jar;.\Sources"
set java="win-jre\bin\java.exe"

FOR %%P IN (%PATH%) DO (
	IF EXIST %%P\java.exe (
		set java="java.exe" ) )

%java% -Dpython.home="jython-2.2.1" -Xmx512m -classpath %classpath% JESstartup

