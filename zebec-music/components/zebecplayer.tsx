import {FunctionComponent, ReactComponentElement} from "react";

type ZebecPlayerProps = {
    url: string,
    sender: string,
    pda: string,
}

const ZebecPlayer: FunctionComponent<ZebecPlayerProps> = (
    {url, sender, pda}
) => {
    return (
        <>
            <audio controls preload="none">
                <source src={`${url}?sender=${sender}&pda=${pda}`} type="audio/mpeg"/>
            </audio>
        </>
    )
}

export default ZebecPlayer;