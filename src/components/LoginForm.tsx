import {
  ButtonItem,
  PanelSection,
  PanelSectionRow,
  ServerAPI,
  TextField,
} from "decky-frontend-lib";
import { RefCallback, useEffect, useState, VFC } from "react";

interface LoginForm {
  email: string;
  password: string;
  authCode: string;
}

const LoginForm: VFC<{
  serverAPI: ServerAPI;
  onLogin: RefCallback<void>;
}> = ({ serverAPI, onLogin }) => {
  const [status, setStatus] = useState<string>();
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [authCode, setAuthCode] = useState<string>("");
  const [ableToSubmit, setAbleToSubmit] = useState(false);

  useEffect(() => {
    setAbleToSubmit(email != "" && password != "" && status != "waiting");
  }, [email, password, status]);

  function formLogin() {
    setStatus("waiting");
    serverAPI
      .callPluginMethod<LoginForm, string>("login", {
        email: email,
        password: password,
        authCode: authCode,
      })
      .then((data) => {
        setStatus(data.result);
        if (data.result == "logged_in") {
          onLogin();
        }
      });
  }

  if (status == "logged_in") {
    return (
      <PanelSection title="Login">
        <PanelSectionRow>Logged in</PanelSectionRow>
      </PanelSection>
    );
  }

  if (status == "waiting") {
    return (
      <PanelSection title="Login">
        <PanelSectionRow>Logging in...</PanelSectionRow>
      </PanelSection>
    );
  }

  return (
    <PanelSection title="Login">
      {status == "unknown" ? (
        <PanelSectionRow>
          An unknown error occurred, please try again.
        </PanelSectionRow>
      ) : null}
      {status != "" ? <PanelSectionRow>{status}</PanelSectionRow> : null}
      <PanelSectionRow>
        <TextField
          label="Email"
          mustBeEmail
          value={email}
          onChange={(e) => setEmail(e?.target.value)}
        />
      </PanelSectionRow>
      <PanelSectionRow>
        <TextField
          label="Password"
          bIsPassword
          value={password}
          onChange={(e) => setPassword(e?.target.value)}
        />
      </PanelSectionRow>
      <PanelSectionRow>
        <TextField
          label="Authenticator Code"
          description="(Optional)"
          value={authCode}
          onChange={(e) => setAuthCode(e?.target.value)}
        />
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem onClick={formLogin} disabled={!ableToSubmit}>
          Login
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
};

export default LoginForm;
