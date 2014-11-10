<?php
if (isset ($_COOKIE['userId'])){
	header('Location:/status/index.php');
	die;
}
$error = 0;
if (isset($_POST) && $_POST['userName']) {
	$name = isset ($_POST ['userName']) ? $_POST ['userName'] : '';
	$pwd = isset ($_POST ['passWord']) ? $_POST ['passWord'] : '';
	
	if ($name == 'admin' && $pwd == 'admin'){
		setcookie('userId','1');
		header('Location:/status/index.php');
		die;
	}else
		$error = 1;
}

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh-cn">

  <head>
    <meta content="charset=utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Avalon AMS login</title>

    <!-- Bootstrap -->
    <link href="css/bootstrap.min.css" rel="stylesheet">
    <link href="css/style.css" rel="stylesheet">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
    <script src="js/jquery.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script>
    $(document).ready(function(){
        $('form').submit(function(){
            if ($('input[name="userName"]').val().trim() == '' || $('input[name="passWord"]').val().trim() == '') {
                return false;
			}
            return true;
		});
	});
    </script>
  </head>
  <body>
  	<div class="row">
  		<div class="logo_div">
  			<center>
	  			<img src="img/avalon_logo.png" />
  			</center>
  		</div>
  		<div class="login_div">
  			<form action='' method='post'>
				Username
				<br />
				<input name='userName' value='' type='text' />
				<br />
				Password
				<br />
				<input name='passWord' value='' type='password' />
				<br />
				<?php if ($error) {?>
			  		<div class='login_error'>帐号密码错误</div>
				<?php }?>
				<input type='submit' value='Log In' class='submit' />
			</form>
  		</div>
  		<div class="clear"></div>
	</div>
  </body>
</html>
