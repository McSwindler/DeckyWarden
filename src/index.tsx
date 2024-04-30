import {
  definePlugin,
  DialogButton,
  Navigation,
  PanelSection,
  PanelSectionRow,
  ServerAPI,
  staticClasses,
} from "decky-frontend-lib";
import { useEffect, useState, VFC } from "react";
import { FaShieldAlt } from "react-icons/fa";
import LoginForm from "./components/LoginForm";

interface StatusResult {
  serverUrl: string;
  lastSync: Date;
  userEmail: string;
  userId: string;
  status: string;
}

const Content: VFC<{ serverAPI: ServerAPI }> = ({ serverAPI }) => {
  const [status, setStatus] = useState<StatusResult>();
  const [error, setError] = useState<string>();

  const loadStatus = () => {
    serverAPI
      .callPluginMethod<{}, StatusResult>("status", {})
      .then((data) =>
        data.success ? setStatus(data.result) : setError(data.result)
      );
  };

  useEffect(loadStatus, []);

  if (status) {
    if (status.status == "unauthenticated") {
      return <LoginForm serverAPI={serverAPI} onLogin={loadStatus} />;
    }
    if (status.status == "locked") {
      return (
        <PanelSection title="Unlock">
          <PanelSectionRow>Insert master password Form Here</PanelSectionRow>
        </PanelSection>
      );
    }
    return (
      <PanelSection title="DeckyWarden">
        <PanelSectionRow>Search/List Secrets</PanelSectionRow>
      </PanelSection>
    );
  }

  if (error) {
    return (
      <PanelSection title="Error">
        <PanelSectionRow>
          <pre>{error}</pre>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  return (
    <PanelSection title="Loading...">
      <PanelSectionRow>
        (pretend there's a fancy spinny graphic here)
      </PanelSectionRow>
    </PanelSection>
  );
};

const DeckyPluginRouterTest: VFC = () => {
  return (
    <div style={{ marginTop: "50px", color: "white" }}>
      Hello World!
      <DialogButton onClick={() => Navigation.NavigateToLibraryTab()}>
        Go to Library
      </DialogButton>
    </div>
  );
};

export default definePlugin((serverApi: ServerAPI) => {
  serverApi.routerHook.addRoute("/decky-plugin-test", DeckyPluginRouterTest, {
    exact: true,
  });

  return {
    title: <div className={staticClasses.Title}>DeckyWarden</div>,
    content: <Content serverAPI={serverApi} />,
    icon: <FaShieldAlt />,
    onDismount() {
      serverApi.routerHook.removeRoute("/decky-plugin-test");
    },
  };
});
