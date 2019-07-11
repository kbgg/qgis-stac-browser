build:
	pb_tool deploy -y
	pb_tool zip --quick

lint:
	flake8
